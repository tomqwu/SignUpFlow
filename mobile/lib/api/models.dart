// Minimal hand-rolled models for the endpoints PR 7.2 needs.
// Will be replaced by generated dart-dio + built_value classes once
// `make mobile-codegen` runs (Java required — see Makefile).

class LoginRequest {
  const LoginRequest({required this.email, required this.password});
  final String email;
  final String password;

  Map<String, dynamic> toJson() => {'email': email, 'password': password};
}

class LoginResponse {
  const LoginResponse({
    required this.token,
    required this.personId,
    required this.email,
    required this.roles,
  });

  final String token;
  final String personId;
  final String email;
  final List<String> roles;

  factory LoginResponse.fromJson(Map<String, dynamic> json) {
    final person = (json['person'] as Map<String, dynamic>?) ?? json;
    final roles = (person['roles'] as List<dynamic>?) ?? const <dynamic>[];
    return LoginResponse(
      token: json['token']?.toString() ?? json['access_token']?.toString() ?? '',
      personId: person['id']?.toString() ?? '',
      email: person['email']?.toString() ?? '',
      roles: roles.map((r) => r.toString()).toList(),
    );
  }
}

class PersonMe {
  const PersonMe({
    required this.id,
    required this.name,
    required this.email,
    required this.orgId,
    required this.roles,
  });

  final String id;
  final String name;
  final String email;
  final String orgId;
  final List<String> roles;

  factory PersonMe.fromJson(Map<String, dynamic> json) {
    final roles = (json['roles'] as List<dynamic>?) ?? const <dynamic>[];
    return PersonMe(
      id: json['id']?.toString() ?? '',
      name: json['name']?.toString() ?? '',
      email: json['email']?.toString() ?? '',
      orgId: json['org_id']?.toString() ?? '',
      roles: roles.map((r) => r.toString()).toList(),
    );
  }
}
