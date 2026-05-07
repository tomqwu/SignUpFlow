// POST /auth/login — returns JWT + role claim.

import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:signupflow_mobile/api/api_client.dart';
import 'package:signupflow_mobile/api/models.dart';

class AuthApi {
  AuthApi(this._dio);
  final Dio _dio;

  Future<LoginResponse> login(LoginRequest req) async {
    final res = await _dio.post<Map<String, dynamic>>(
      '/auth/login',
      data: req.toJson(),
    );
    if (res.data == null) {
      throw const FormatException('empty /auth/login response');
    }
    return LoginResponse.fromJson(res.data!);
  }
}

final authApiProvider = Provider<AuthApi>((ref) {
  return AuthApi(ref.watch(dioProvider));
});
