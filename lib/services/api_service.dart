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
    } else {
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

  // NEW: AI Prediction Method
  static Future<Map<String, dynamic>> predictSynthesis(
    String baseMaterial,
    String targetMaterial,
    String targetPhase,
  ) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/predict'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'user_id':
              1, // Hardcoded for testing; we will make this dynamic later
          'base_material': baseMaterial,
          'target_material': targetMaterial,
          'target_phase': targetPhase.isEmpty ? 'synthesis' : targetPhase,
        }),
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body); // Returns the 766.5°C and other data!
      } else {
        return {
          'error': jsonDecode(response.body)['error'] ?? 'Simulation failed',
        };
      }
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
