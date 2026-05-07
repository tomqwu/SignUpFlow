// Wraps the generated `SignupflowApi` (from package:signupflow_api) with our
// dio + auth interceptor + base URL. Provides one Riverpod provider for the
// generated client; `lib/auth/login_repository.dart` and other call sites
// access the typed APIs through `ref.watch(signupflowApiProvider)`.

import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:signupflow_api/signupflow_api.dart';
import 'package:signupflow_mobile/auth/secure_token_storage.dart';

const String defaultApiBaseUrl = String.fromEnvironment(
  'API_BASE_URL',
  // Generated paths already include `/api/v1` (taken from the OpenAPI spec),
  // so the base URL is the bare host.
  defaultValue: 'http://localhost:8000',
);

/// dio configured with the API base URL + a token interceptor.
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
        // 401 → wipe token; router redirect handles bounce to /login.
        if (e.response?.statusCode == 401) {
          await storage.clearToken();
        }
        handler.next(e);
      },
    ),
  );

  return dio;
});

/// The generated typed API client. Construct call sites via
/// `ref.watch(signupflowApiProvider).getAuthApi()` etc.
final signupflowApiProvider = Provider<SignupflowApi>((ref) {
  return SignupflowApi(dio: ref.watch(dioProvider));
});
