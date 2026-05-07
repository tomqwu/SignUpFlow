// Hand-rolled dio client for the endpoints PR 7.2 needs (login + people/me).
//
// Note: this file lives at mobile/lib/api/ so it'll be REPLACED by generated
// code once `make mobile-codegen` is run with Java available. Keep the public
// surface (api_client provider, AuthApi, PeopleApi) compatible so the swap
// is mechanical.
//
// Until then, any new endpoint added here must be done by hand and tracked
// against tests/contract/openapi.snapshot.json so signatures stay in sync.

import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:signupflow_mobile/auth/secure_token_storage.dart';

const String defaultApiBaseUrl = String.fromEnvironment(
  'API_BASE_URL',
  defaultValue: 'http://localhost:8000/api/v1',
);

/// Provides a dio instance configured with the API base URL + a token
/// interceptor that adds `Authorization: Bearer <jwt>` from secure storage.
final dioProvider = Provider<Dio>((ref) {
  final storage = ref.watch(secureTokenStorageProvider);
  final dio = Dio(BaseOptions(
    baseUrl: defaultApiBaseUrl,
    connectTimeout: const Duration(seconds: 10),
    receiveTimeout: const Duration(seconds: 30),
    contentType: 'application/json',
    headers: <String, dynamic>{'Accept': 'application/json'},
  ));

  dio.interceptors.add(
    InterceptorsWrapper(
      onRequest: (options, handler) async {
        final token = await storage.readToken();
        if (token != null && token.isNotEmpty) {
          options.headers['Authorization'] = 'Bearer $token';
        }
        handler.next(options);
      },
      onError: (e, handler) async {
        // 401 → wipe token; router redirect handles the bounce to /login.
        if (e.response?.statusCode == 401) {
          await storage.clearToken();
        }
        handler.next(e);
      },
    ),
  );

  return dio;
});
