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

/// Outcome of one /auth/refresh attempt. The interceptor must distinguish
/// "refresh failed" (wipe storage) from "refresh succeeded but storage was
/// mutated mid-flight" (leave storage alone) — otherwise a signOut / fresh
/// login that races a stale refresh response gets clobbered.
enum _RefreshOutcome { success, failure, stale }

/// Pump a single concurrent /auth/refresh attempt. If two requests hit
/// 401 at the same time, only one fires the refresh; the others await
/// the same `Future` and replay against the new token.
Completer<_RefreshOutcome>? _refreshInFlight;

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

        final outcome = await _attemptRefresh(dio, storage);
        if (outcome == _RefreshOutcome.failure) {
          // No refresh token, refresh failed, or 401 from /auth/refresh
          // itself — wipe both tokens and let the router bounce to /login.
          await storage.clearAll();
          handler.next(e);
          return;
        }
        if (outcome == _RefreshOutcome.stale) {
          // Storage was mutated (signOut / fresh login) while /auth/refresh
          // was in flight. Don't replay with the dropped tokens, but also
          // don't clear the user's current session — leave storage alone.
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
/// concurrent calls so only one round-trip happens at a time. The
/// outcome tells the caller whether to (success) replay the original
/// request, (failure) clear storage and propagate 401, or (stale) just
/// propagate 401 without touching storage.
Future<_RefreshOutcome> _attemptRefresh(Dio dio, SecureTokenStorage storage) async {
  // Coalesce concurrent refreshes.
  final inFlight = _refreshInFlight;
  if (inFlight != null) {
    return inFlight.future;
  }
  final completer = Completer<_RefreshOutcome>();
  _refreshInFlight = completer;

  // Snapshot the storage generation at the start. Any storage mutation
  // (signOut, fresh login, another refresh landing first) bumps it;
  // we check before persisting so an in-flight stale response can't
  // overwrite whatever's currently in storage. Hoisted out of the try
  // block so the DioException catch can also see it (Dart scoping).
  final genAtStart = storage.sessionGeneration;

  try {
    final refreshToken = await storage.readRefreshToken();
    if (refreshToken == null || refreshToken.isEmpty) {
      completer.complete(_RefreshOutcome.failure);
      return _RefreshOutcome.failure;
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
      // Drop the response if anything mutated storage during the
      // /auth/refresh round-trip — the response is for a session
      // that's already been replaced or cleared. KNOWN RESIDUAL RACE:
      // within Dart's single-isolate cooperative model, between the
      // two awaited writes below another mutator can interleave. We
      // don't attempt to roll back the first write, because by the
      // time we detect it the "current" access token may belong to a
      // fresh login that ran after our write — clearing it would log
      // that user out. The realistic window is platform-call latency
      // (microseconds); on the next 401 the interceptor sees whatever
      // session is actually in storage and rotates from there.
      if (storage.sessionGeneration != genAtStart) {
        completer.complete(_RefreshOutcome.stale);
        return _RefreshOutcome.stale;
      }
      await storage.writeToken(body['token'] as String);
      await storage.writeRefreshToken(body['refresh_token'] as String);
      completer.complete(_RefreshOutcome.success);
      return _RefreshOutcome.success;
    }
    completer.complete(_RefreshOutcome.failure);
    return _RefreshOutcome.failure;
  } on DioException {
    // If the refresh failed AND storage changed since we started, the
    // failure belongs to a session that's already gone. Don't make the
    // caller clearAll() — that would wipe the new session.
    if (storage.sessionGeneration != genAtStart) {
      completer.complete(_RefreshOutcome.stale);
      return _RefreshOutcome.stale;
    }
    completer.complete(_RefreshOutcome.failure);
    return _RefreshOutcome.failure;
  } finally {
    _refreshInFlight = null;
  }
}

/// The generated typed API client. Construct call sites via
/// `ref.watch(signupflowApiProvider).getAuthApi()` etc.
final signupflowApiProvider = Provider<SignupflowApi>((ref) {
  return SignupflowApi(dio: ref.watch(dioProvider));
});
