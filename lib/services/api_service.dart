import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;

class ApiService {
  // Use 10.0.2.2 for Android Emulators to hit your local Python server.
  // If using iOS Simulator, use 127.0.0.1.
  // For web: localhost should work, but make sure CORS is enabled on the backend.
  static String get baseUrl {
    if (kIsWeb) {
      return 'http://localhost:5000/api';
    }

    switch (defaultTargetPlatform) {
      case TargetPlatform.android:
        return 'http://10.0.2.2:5000/api';
      case TargetPlatform.iOS:
      case TargetPlatform.macOS:
      case TargetPlatform.windows:
      case TargetPlatform.linux:
      case TargetPlatform.fuchsia:
        return 'http://127.0.0.1:5000/api';
    }
  }

  static Future<Map<String, dynamic>> login(
    String email,
    String password,
  ) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/login'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'email': email, 'password': password}),
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        // Backend returned an error (e.g., 401 Unauthorized)
        return {'error': jsonDecode(response.body)['error'] ?? 'Login failed'};
      }
    } catch (e) {
      return {'error': 'Failed to connect to the server. Is Flask running?'};
    }
  }

  // ... (keep your existing baseUrl and login method) ...

  // NEW: Registration Method
  static Future<Map<String, dynamic>> register(
    String name,
    String email,
    String password,
  ) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/register'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'username': name,
          'email': email,
          'password': password,
        }),
      );

      // 201 Created is the standard HTTP status for a successful registration
      if (response.statusCode == 200 || response.statusCode == 201) {
        return jsonDecode(response.body);
      } else {
        return {
          'error': jsonDecode(response.body)['error'] ?? 'Registration failed',
        };
      }
    } catch (e) {
      return {'error': 'Failed to connect to the server. Is Flask running?'};
    }
  }

  static Map<String, dynamic> _decodeJsonBody(http.Response response) {
    try {
      final decoded = jsonDecode(response.body);
      if (decoded is Map<String, dynamic>) {
        return decoded;
      }
      if (decoded is Map) {
        return Map<String, dynamic>.from(decoded);
      }
      return {'data': decoded};
    } catch (_) {
      return <String, dynamic>{};
    }
  }

  static Map<String, dynamic> _responseError(
    http.Response response,
    String fallbackMessage,
  ) {
    final payload = _decodeJsonBody(response);
    return {
      ...payload,
      'status_code': response.statusCode,
      'error': payload['error'] ?? payload['message'] ?? fallbackMessage,
    };
  }

  static Map<String, dynamic> _normalizeSynthesisPayload(
    Map<String, dynamic> payload,
  ) {
    final nested = payload['synthesis_result'];
    final nestedMap = nested is Map
        ? Map<String, dynamic>.from(nested)
        : <String, dynamic>{};

    final feasible = payload['feasible'] ?? nestedMap['feasible'];
    final optimalTemperature =
        payload['optimal_temperature_c'] ??
        payload['optimal_temp_c'] ??
        payload['required_temperature_c'] ??
        nestedMap['optimal_temperature_c'] ??
        nestedMap['optimal_temp_c'] ??
        nestedMap['required_temperature_c'];

    final achievableProduct =
        payload['achievable_product'] ??
        payload['achievable_compound'] ??
        nestedMap['achievable_product'] ??
        nestedMap['achievable_compound'];

    final confidenceScore =
        payload['confidence_score'] ??
        payload['confidence_pct'] ??
        nestedMap['confidence_score'] ??
        nestedMap['confidence_pct'];

    final message = payload['message'] ?? nestedMap['message'];
    final reason = payload['reason'] ?? nestedMap['reason'];
    final recommendations =
        payload['recommendations'] ?? nestedMap['recommendations'];
    final notes = payload['notes'] ?? nestedMap['notes'];

    return {
      ...payload,
      if (nestedMap.isNotEmpty) 'synthesis_result': nestedMap,
      'feasible': feasible == true,
      if (optimalTemperature != null)
        'optimal_temperature_c': optimalTemperature,
      if (achievableProduct != null) 'achievable_product': achievableProduct,
      if (confidenceScore != null) 'confidence_score': confidenceScore,
      if (message != null) 'message': message,
      if (reason != null) 'reason': reason,
      if (recommendations != null) 'recommendations': recommendations,
      if (notes != null) 'notes': notes,
    };
  }

  static Future<Map<String, dynamic>> checkSynthesisFeasibility(
    String baseMaterial,
    String targetMaterial,
  ) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/synthesis/check'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'base_material': baseMaterial,
          'target_material': targetMaterial,
        }),
      );

      final payload = _decodeJsonBody(response);

      if (response.statusCode == 200) {
        return {
          ..._normalizeSynthesisPayload(payload),
          'status_code': response.statusCode,
        };
      }

      if (response.statusCode == 400) {
        return {
          ..._normalizeSynthesisPayload(payload),
          'status_code': response.statusCode,
        };
      }

      return _responseError(response, 'Feasibility check failed');
    } catch (e) {
      return {'error': 'Failed to connect to the server.'};
    }
  }

  // NEW: AI Prediction Method
  static Future<Map<String, dynamic>> predictSynthesis({
    int? userId,
    required String baseMaterial,
    required String targetMaterial,
    String targetPhase = 'synthesis',
  }) async {
    try {
      final body = <String, dynamic>{
        'base_material': baseMaterial,
        'target_material': targetMaterial,
        'target_phase': targetPhase.isEmpty ? 'synthesis' : targetPhase,
      };

      if (userId != null) {
        body['user_id'] = userId;
      }

      final response = await http.post(
        Uri.parse('$baseUrl/predict'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(body),
      );

      final payload = _decodeJsonBody(response);

      if (response.statusCode == 200) {
        return {
          ..._normalizeSynthesisPayload(payload),
          'status_code': response.statusCode,
        };
      }

      if (response.statusCode == 400) {
        return {
          ..._normalizeSynthesisPayload(payload),
          'status_code': response.statusCode,
        };
      }

      return _responseError(response, 'Simulation failed');
    } catch (e) {
      return {'error': 'Failed to connect to the server.'};
    }
  }

  static Future<Map<String, dynamic>> fetchHistory(int userId) async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/history/$userId'));

      if (response.statusCode == 200) {
        return _decodeJsonBody(response);
      }

      return {
        'error':
            _decodeJsonBody(response)['error'] ?? 'Failed to fetch history',
      };
    } catch (e) {
      return {'error': 'Failed to connect to the server.'};
    }
  }

  // NEW: Logout Method
  static Future<Map<String, dynamic>> logout(int userId) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/logout'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'user_id': userId}),
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        return {'error': jsonDecode(response.body)['error'] ?? 'Logout failed'};
      }
    } catch (e) {
      return {'error': 'Failed to connect to the server.'};
    }
  }
}
