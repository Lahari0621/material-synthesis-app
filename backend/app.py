from contextlib import contextmanager
from datetime import date, datetime
from decimal import Decimal
import os
import threading

# Keep BLAS/OpenMP from oversubscribing under Waitress thread concurrency.
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")

from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from mysql.connector import pooling
from mysql.connector.errors import Error as MySQLError

from master_predictor import predict_advanced_temperature
from synthesis_predictor import (
    predict_material_synthesis,
    normalize_material_name,
    get_transformation_map,
)

app = Flask(__name__)
CORS(app)

# Bound concurrent model inference so 100 VUs don't thrash the GIL.
ML_SEMAPHORE = threading.BoundedSemaphore(8)

# Database Configuration + connection pool for concurrent load
# Override via env for GitHub Actions / local Docker MySQL.
db_config = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", "Chaithu@123"),
    "database": os.environ.get("DB_NAME", "furnace_db"),
    "autocommit": False,
    "connection_timeout": 10,
}

db_pool = pooling.MySQLConnectionPool(
    pool_name="furnace_pool",
    pool_size=int(os.environ.get("DB_POOL_SIZE", "32")),
    pool_reset_session=True,
    **db_config,
)


@contextmanager
def db_cursor(dictionary=False):
    """Borrow a pooled connection and always return it."""
    conn = None
    cursor = None
    try:
        conn = db_pool.get_connection()
        cursor = conn.cursor(dictionary=dictionary)
        yield conn, cursor
        conn.commit()
    except Exception:
        if conn is not None and conn.is_connected():
            conn.rollback()
        raise
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None and conn.is_connected():
            conn.close()


def json_safe(value):
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, list):
        return [json_safe(item) for item in value]
    if isinstance(value, dict):
        return {key: json_safe(item) for key, item in value.items()}
    return value


@app.route("/api/health", methods=["GET"])
def health():
    try:
        with db_cursor() as (conn, cursor):
            cursor.execute("SELECT 1")
            cursor.fetchone()
        return jsonify({"status": "ok", "database": "ready"}), 200
    except MySQLError as exc:
        return jsonify({"status": "degraded", "database": str(exc)}), 503


# ==========================================
# AUTHENTICATION ROUTES
# ==========================================

@app.route("/api/register", methods=["POST"])
def register():
    try:
        data = request.get_json(silent=True) or {}
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")

        if not username or not email or not password:
            return jsonify({"error": "Username, email, and password are required"}), 400

        hashed_password = generate_password_hash(password)

        with db_cursor() as (conn, cursor):
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                return jsonify({"error": "Email already registered"}), 409

            query = (
                "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)"
            )
            cursor.execute(query, (username, email, hashed_password))
            new_user_id = cursor.lastrowid

        return jsonify(
            {
                "message": "User registered successfully!",
                "user": {"id": new_user_id, "username": username, "email": email},
            }
        ), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/login", methods=["POST"])
def login():
    try:
        data = request.get_json(silent=True) or {}
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        with db_cursor(dictionary=True) as (conn, cursor):
            cursor.execute(
                "SELECT id, username, email, password_hash FROM users WHERE email = %s",
                (email,),
            )
            user = cursor.fetchone()

        if user and check_password_hash(user["password_hash"], password):
            return jsonify(
                {
                    "message": "Login successful",
                    "user": {
                        "id": user["id"],
                        "username": user["username"],
                        "email": user["email"],
                    },
                }
            ), 200

        return jsonify({"error": "Invalid email or password"}), 401

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/logout", methods=["POST"])
def logout():
    try:
        data = request.get_json(silent=True) or {}
        user_id = data.get("user_id")

        if not user_id:
            return jsonify({"error": "user_id is required"}), 400

        return jsonify({"message": "Logout successful", "user_id": user_id}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==========================================
# PREDICTION ROUTE
# ==========================================
@app.route("/api/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json(silent=True) or {}

        user_id = data.get("user_id")
        base_material = data.get("base_material")
        target_material = data.get("target_material")

        if not base_material or not target_material:
            return jsonify(
                {"error": "base_material and target_material are required"}
            ), 400

        base_material = normalize_material_name(base_material)
        target_material = normalize_material_name(target_material)
        has_user_id = user_id is not None

        # Material synthesis path
        if base_material.lower() != target_material.lower():
            with ML_SEMAPHORE:
                synthesis_result = predict_material_synthesis(
                    base_material, target_material
                )

            if synthesis_result.get("success"):
                optimal_temp = synthesis_result["required_temperature_c"]
                confidence = synthesis_result["confidence_pct"]
                achievable_product = synthesis_result.get(
                    "achievable_compound", target_material
                )
                notes = f"Synthesis feasible: {base_material} -> {achievable_product}"
            else:
                optimal_temp = 0
                confidence = 0
                achievable_product = "Not Feasible"
                notes = synthesis_result.get("reason", "Transformation not feasible")

            history_id = None
            if has_user_id:
                with db_cursor() as (conn, cursor):
                    history_query = """
                        INSERT INTO prediction_history
                        (user_id, base_material, target_material, optimal_temp_c,
                         heating_duration_min, confidence_score)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(
                        history_query,
                        (
                            user_id,
                            base_material,
                            target_material,
                            optimal_temp,
                            45,
                            confidence,
                        ),
                    )
                    history_id = cursor.lastrowid

            return jsonify(
                {
                    "history_id": history_id,
                    "synthesis_result": synthesis_result,
                    "status": "success"
                    if synthesis_result.get("success")
                    else "not_feasible",
                    "optimal_temperature_c": optimal_temp,
                    "achievable_product": achievable_product,
                    "confidence_score": confidence,
                    "notes": notes,
                }
            ), 200 if synthesis_result.get("success") else 400

        # Phase transformation path (same material)
        target_phase = data.get("target_phase", "synthesis").lower()
        normalized_target_material = normalize_material_name(target_material)

        with db_cursor(dictionary=True) as (conn, cursor):
            cursor.execute(
                "SELECT * FROM material_catalog WHERE material_name = %s",
                (normalized_target_material,),
            )
            cached_props = cursor.fetchone()

            if cached_props:
                melting_point = float(cached_props["melting_point_c"])
                density = float(cached_props["density_g_cm3"])
                specific_heat = float(cached_props["specific_heat_j_kg_k"])
            else:
                try:
                    from mendeleev import element

                    el = element(normalized_target_material)
                    melting_point = (
                        float(el.melting_point) - 273.15 if el.melting_point else 1000.0
                    )
                    density = float(el.density)
                    specific_heat = (
                        float(el.specific_heat) * 1000 if el.specific_heat else 500.0
                    )

                    cache_query = """
                        INSERT INTO material_catalog
                        (material_name, melting_point_c, density_g_cm3, specific_heat_j_kg_k)
                        VALUES (%s, %s, %s, %s)
                    """
                    cursor.execute(
                        cache_query,
                        (
                            normalized_target_material,
                            melting_point,
                            density,
                            specific_heat,
                        ),
                    )
                except Exception:
                    return jsonify(
                        {
                            "error": (
                                f"Could not find properties for '{target_material}'. "
                                "It may be a complex alloy not in the elemental database."
                            )
                        }
                    ), 404

            with ML_SEMAPHORE:
                ai_result = predict_advanced_temperature(
                    density=density,
                    specific_heat=specific_heat,
                    target_phase=target_phase,
                    target_conversion=98.0,
                )

            if "error" in ai_result:
                return jsonify(ai_result), 404

            optimal_temp_c = ai_result["optimal_temp_c"]
            heating_duration_min = 45
            confidence_score = ai_result["confidence_score"]
            notes = ai_result.get("notes", "")

            history_id = None
            if has_user_id:
                history_query = """
                    INSERT INTO prediction_history
                    (user_id, base_material, target_material, optimal_temp_c,
                     heating_duration_min, confidence_score)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(
                    history_query,
                    (
                        user_id,
                        base_material,
                        target_material,
                        optimal_temp_c,
                        heating_duration_min,
                        confidence_score,
                    ),
                )
                history_id = cursor.lastrowid

        prediction = {
            "history_id": history_id,
            "optimal_temperature_c": optimal_temp_c,
            "heating_duration_min": heating_duration_min,
            "ramp_rate_c_per_min": 15.0,
            "confidence_score": confidence_score,
            "notes": f"{notes} Data dynamically fetched & cached.",
        }
        return jsonify(prediction), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==========================================
# MATERIAL SYNTHESIS ENDPOINT
# ==========================================
@app.route("/api/synthesis/check", methods=["POST"])
def check_synthesis():
    try:
        data = request.get_json(silent=True) or {}

        base_material = data.get("base_material")
        target_material = data.get("target_material")

        if not base_material or not target_material:
            return jsonify(
                {"error": "base_material and target_material are required"}
            ), 400

        base_material = normalize_material_name(base_material)
        target_material = normalize_material_name(target_material)

        with ML_SEMAPHORE:
            result = predict_material_synthesis(base_material, target_material)

        if result.get("success"):
            return jsonify(
                {
                    "feasible": True,
                    "base_material": base_material,
                    "target_material": target_material,
                    "achievable_product": result.get("achievable_compound"),
                    "required_temperature_c": result.get("required_temperature_c"),
                    "confidence_pct": result.get("confidence_pct"),
                    "instructions": result.get("instructions"),
                    "notes": result.get("notes"),
                }
            ), 200

        return jsonify(
            {
                "feasible": False,
                "base_material": base_material,
                "target_material": target_material,
                "message": result.get("message", "Not feasible"),
                "reason": result.get("reason"),
                "recommendations": result.get("recommendations", []),
            }
        ), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/synthesis/alternatives/<base_material>", methods=["GET"])
def get_synthesis_alternatives(base_material):
    try:
        transformation_map = get_transformation_map()
        base_key = normalize_material_name(base_material).lower()
        alternatives = []

        for trans_key, trans_info in transformation_map.items():
            if not trans_info["is_feasible"]:
                continue
            parts = trans_key.split("_to_")
            if len(parts) == 2 and parts[0] == base_key:
                alternatives.append(
                    {
                        "target_material": parts[1].upper(),
                        "achievable_product": trans_info["target_compound"],
                        "required_temperature_c": trans_info["required_temp"],
                        "confidence_pct": trans_info["confidence"],
                        "notes": trans_info["notes"],
                    }
                )

        if not alternatives:
            return jsonify(
                {
                    "base_material": base_material,
                    "feasible_alternatives": [],
                    "message": "No feasible transformations found",
                }
            ), 404

        alternatives.sort(key=lambda x: x["required_temperature_c"])
        return jsonify(
            {
                "base_material": base_material,
                "feasible_alternatives": alternatives,
                "count": len(alternatives),
            }
        ), 200

    except FileNotFoundError:
        return jsonify(
            {"error": "Model files not found. Please train the synthesis model first."}
        ), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/history/<int:user_id>", methods=["GET"])
def get_history(user_id):
    try:
        with db_cursor(dictionary=True) as (conn, cursor):
            query = """
                SELECT id, base_material, target_material, optimal_temp_c,
                       heating_duration_min, confidence_score, created_at
                FROM prediction_history
                WHERE user_id = %s
                ORDER BY created_at DESC
                LIMIT 100
            """
            cursor.execute(query, (user_id,))
            history = cursor.fetchall()

        return jsonify({"history": json_safe(history)}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # Prefer Waitress for concurrent baseline/load traffic on Windows.
    try:
        from waitress import serve

        print(
            "Starting production server with Waitress on http://0.0.0.0:5000",
            flush=True,
        )
        serve(
            app,
            host="0.0.0.0",
            port=5000,
            threads=32,
            channel_timeout=120,
            connection_limit=200,
            backlog=256,
        )
    except ImportError:
        print(
            "Waitress not installed; falling back to Flask threaded server.",
            flush=True,
        )
        app.run(debug=False, host="0.0.0.0", port=5000, threaded=True)
