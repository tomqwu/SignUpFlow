// Wraps the generated `SignupflowApi` (from package:signupflow_api) with our
// dio + auth interceptor + base URL. Provides one Riverpod provider for the
// generated client; `lib/auth/login_repository.dart` and other call sites
// access the typed APIs through `ref.watch(signupflowApiProvider)`.

import 'dart:async';

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

/// Pump a single concurrent /auth/refresh attempt. If two requests hit
/// 401 at the same time, only one fires the refresh; the others await
/// the same `Future` and replay against the new token.
Completer<bool>? _refreshInFlight;

/// dio configured with the API base URL + a token-refresh interceptor.
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
        // Only handle 401 from non-refresh endpoints; everything else
        // passes through.
        if (e.response?.statusCode != 401 ||
            e.requestOptions.path.endsWith('/auth/refresh') ||
            e.requestOptions.extra['__retry'] == true) {
          handler.next(e);
          return;
        }

        final refreshed = await _attemptRefresh(dio, storage);
        if (!refreshed) {
          // No refresh token, refresh failed, or 401 from /auth/refresh
          // itself — wipe both tokens and let the router bounce to /login.
          await storage.clearAll();
          handler.next(e);
          return;
        }

        // Replay the original request with the new access token.
        try {
          final newToken = await storage.readToken();
          final retryOptions = e.requestOptions
            ..headers['Authorization'] =
                newToken != null ? 'Bearer $newToken' : null
            ..extra['__retry'] = true;
          final replay = await dio.fetch<dynamic>(retryOptions);
          handler.resolve(replay);
        } on DioException catch (replayErr) {
          handler.next(replayErr);
        }
      },
    ),
  );

  return dio;
});

/// Fires `/auth/refresh` against the stored refresh token. Coalesces
/// concurrent calls so only one round-trip happens at a time. Returns
/// true on success (new tokens persisted), false otherwise.
Future<bool> _attemptRefresh(Dio dio, SecureTokenStorage storage) async {
  // Coalesce concurrent refreshes.
  final inFlight = _refreshInFlight;
  if (inFlight != null) {
    return inFlight.future;
  }
  final completer = Completer<bool>();
  _refreshInFlight = completer;

  try {
    final refreshToken = await storage.readRefreshToken();
    if (refreshToken == null || refreshToken.isEmpty) {
      completer.complete(false);
      return false;
    }
    final res = await dio.post<dynamic>(
      '/api/v1/auth/refresh',
      data: <String, String>{'refresh_token': refreshToken},
      options: Options(
        // Don't attach the (likely-expired) Bearer token to the refresh call;
        // the endpoint authenticates via the body's refresh_token.
        headers: <String, dynamic>{'Authorization': null},
        // Avoid the interceptor recursing on a 401 from /auth/refresh itself.
        extra: <String, dynamic>{'__retry': true},
      ),
    );
    final body = res.data;
    if (body is Map &&
        body['token'] is String &&
        body['refresh_token'] is String) {
      // If signOut() / clearAll() ran while /auth/refresh was in flight,
      // the refresh slot in storage is now empty (or replaced by a fresh
      // login's token). Persisting the response would resurrect the old
      // session after the user explicitly logged out. Drop the write.
      final stillStored = await storage.readRefreshToken();
      if (stillStored != refreshToken) {
        completer.complete(false);
        return false;
      }
      await storage.writeToken(body['token'] as String);
      await storage.writeRefreshToken(body['refresh_token'] as String);
      completer.complete(true);
      return true;
    }
    completer.complete(false);
    return false;
  } on DioException {
    completer.complete(false);
    return false;
  } finally {
    _refreshInFlight = null;
  }
}

/// The generated typed API client. Construct call sites via
/// `ref.watch(signupflowApiProvider).getAuthApi()` etc.
final signupflowApiProvider = Provider<SignupflowApi>((ref) {
  return SignupflowApi(dio: ref.watch(dioProvider));
});
