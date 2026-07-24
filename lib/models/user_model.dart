class User {
  final int id;
  final String name;
  final String email;

  User({required this.id, required this.name, required this.email});

  factory User.fromJson(Map<String, dynamic> json) {
    final userPayload = json['user'] is Map<String, dynamic>
        ? json['user'] as Map<String, dynamic>
        : json;

    return User(
      id: _toInt(userPayload['user_id'] ?? userPayload['id']),
      name: _toStringValue(
        userPayload['username'] ?? userPayload['name'],
        fallback: 'User',
      ),
      email: _toStringValue(userPayload['email']),
    );
  }

  Map<String, dynamic> toJson() {
    return {'id': id, 'username': name, 'email': email};
  }

  static int _toInt(dynamic value) {
    if (value is int) {
      return value;
    }
    if (value is String) {
      return int.tryParse(value) ?? 0;
    }
    return 0;
  }

  static String _toStringValue(dynamic value, {String fallback = ''}) {
    if (value is String && value.trim().isNotEmpty) {
      return value.trim();
    }
    return fallback;
  }
}
