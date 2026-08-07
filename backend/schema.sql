CREATE DATABASE IF NOT EXISTS furnace_db;
USE furnace_db;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS prediction_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    base_material VARCHAR(100) NOT NULL,
    target_material VARCHAR(100) NOT NULL,
    optimal_temp_c DOUBLE NOT NULL,
    heating_duration_min INT NOT NULL,
    confidence_score DOUBLE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_prediction_user_created (user_id, created_at)
);

CREATE TABLE IF NOT EXISTS material_catalog (
    material_name VARCHAR(100) PRIMARY KEY,
    melting_point_c DOUBLE NOT NULL,
    density_g_cm3 DOUBLE NOT NULL,
    specific_heat_j_kg_k DOUBLE NOT NULL
);

INSERT INTO users (id, username, email, password_hash)
VALUES (1, 'baseline_user', 'baseline@example.com', 'not-used-for-load-test')
ON DUPLICATE KEY UPDATE username = VALUES(username);
