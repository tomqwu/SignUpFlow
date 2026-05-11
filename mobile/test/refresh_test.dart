// dio refresh-interceptor tests — Sprint 9 PR 9.4.
//
// Verifies that:
// - A single 401 on a normal endpoint triggers /auth/refresh, which
//   rotates both tokens and replays the original request.
// - When /auth/refresh itself 401s, both tokens are wiped.
// - When no refresh token is stored, both tokens are wiped immediately.
// - Concurrent 401s only fire one /auth/refresh round-trip
//   (request coalescing).

import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:signupflow_mobile/api/api_client.dart';
import 'package:signupflow_mobile/auth/secure_token_storage.dart';

class _FakeAdapter implements HttpClientAdapter {
  _FakeAdapter(this.handler);

  /// Per-call handler returns the canned (status, body) for each request.
  final Future<ResponseBody> Function(RequestOptions options) handler;
  final List<RequestOptions> calls = [];

  @override
  Future<ResponseBody> fetch(
    RequestOptions options,
    Stream<List<int>>? requestStream,
    Future<void>? cancelFuture,
  ) async {
    calls.add(options);
    return handler(options);
  }

  @override
  void close({bool force = false}) {}
}

ResponseBody _json(int status, String body) => ResponseBody.fromString(
      body,
      status,
      headers: <String, List<String>>{
        Headers.contentTypeHeader: <String>['application/json'],
      },
    );

ProviderContainer _container(SecureTokenStorage storage) =>
    ProviderContainer(overrides: [
      secureTokenStorageProvider.overrideWithValue(storage),
    ]);

void main() {
  test('401 on /events triggers /auth/refresh + replay with new token', () async {
    final storage = InMemoryTokenStorage();
    await storage.writeToken('expired_access');
    await storage.writeRefreshToken('valid_refresh');

    var eventsCalls = 0;
    final adapter = _FakeAdapter((opts) async {
      if (opts.path.endsWith('/auth/refresh')) {
        return _json(
          200,
          '{"token":"new_access","refresh_token":"new_refresh"}',
        );
      }
      eventsCalls++;
      // First call gets 401 (expired), retry succeeds.
      if (eventsCalls == 1) return _json(401, '{"detail":"expired"}');
      return _json(200, '{"items":[]}');
    });

    final container = _container(storage);
    addTearDown(container.dispose);
    final dio = container.read(dioProvider)..httpClientAdapter = adapter;

    final res = await dio.get<dynamic>('/api/v1/events');
    expect(res.statusCode, 200);
    expect(eventsCalls, 2, reason: 'original request should be replayed');
    expect(await storage.readToken(), 'new_access');
    expect(await storage.readRefreshToken(), 'new_refresh');
  });

  test('401 from /auth/refresh wipes both tokens and surfaces the original 401', () async {
    final storage = InMemoryTokenStorage();
    await storage.writeToken('expired_access');
    await storage.writeRefreshToken('stale_refresh');

    final adapter = _FakeAdapter((opts) async {
      if (opts.path.endsWith('/auth/refresh')) {
        return _json(401, '{"detail":"Refresh token superseded"}');
      }
      return _json(401, '{"detail":"expired"}');
    });

    final container = _container(storage);
    addTearDown(container.dispose);
    final dio = container.read(dioProvider)..httpClientAdapter = adapter;

    expect(
      () async => dio.get<dynamic>('/api/v1/events'),
      throwsA(isA<DioException>()),
    );
    // Give the async chain a tick to settle.
    await Future<void>.delayed(const Duration(milliseconds: 10));

    expect(await storage.readToken(), isNull);
    expect(await storage.readRefreshToken(), isNull);
  });

  test('401 with no refresh token wipes access + falls through', () async {
    final storage = InMemoryTokenStorage();
    await storage.writeToken('expired_access');
    // NO refresh token.

    final adapter = _FakeAdapter((opts) async {
      // /auth/refresh should never be called — fail loudly if it is.
      expect(opts.path.endsWith('/auth/refresh'), isFalse);
      return _json(401, '{"detail":"expired"}');
    });

    final container = _container(storage);
    addTearDown(container.dispose);
    final dio = container.read(dioProvider)..httpClientAdapter = adapter;

    expect(
      () async => dio.get<dynamic>('/api/v1/events'),
      throwsA(isA<DioException>()),
    );
    await Future<void>.delayed(const Duration(milliseconds: 10));

    expect(await storage.readToken(), isNull);
  });

  test('refresh in flight when storage is cleared does NOT resurrect tokens', () async {
    // P2 from #82: a 401-triggered /auth/refresh that's mid-flight when
    // signOut()/clearAll() runs must not persist the response, otherwise
    // the user who explicitly logged out gets silently re-authed.
    final storage = InMemoryTokenStorage();
    await storage.writeToken('expired_access');
    await storage.writeRefreshToken('valid_refresh');

    final adapter = _FakeAdapter((opts) async {
      if (opts.path.endsWith('/auth/refresh')) {
        // Delay so we can simulate signOut clearing storage *during* the
        // refresh round-trip.
        await Future<void>.delayed(const Duration(milliseconds: 30));
        return _json(
          200,
          '{"token":"resurrected_access","refresh_token":"resurrected_refresh"}',
        );
      }
      return _json(401, '{"detail":"expired"}');
    });

    final container = _container(storage);
    addTearDown(container.dispose);
    final dio = container.read(dioProvider)..httpClientAdapter = adapter;

    // Kick off the request that triggers refresh.
    final pending = dio.get<dynamic>('/api/v1/events');
    // While refresh is in flight, simulate signOut clearing storage.
    await Future<void>.delayed(const Duration(milliseconds: 10));
    await storage.clearAll();

    // The request itself fails (no valid auth could be restored).
    await expectLater(pending, throwsA(isA<DioException>()));
    await Future<void>.delayed(const Duration(milliseconds: 10));

    // Critical: storage must remain cleared. The refresh response
    // returned new tokens after clearAll(), but the interceptor must
    // detect the storage mismatch and drop the write.
    expect(await storage.readToken(), isNull);
    expect(await storage.readRefreshToken(), isNull);
  });

  test('two concurrent 401s coalesce to a single /auth/refresh call', () async {
    final storage = InMemoryTokenStorage();
    await storage.writeToken('expired_access');
    await storage.writeRefreshToken('valid_refresh');

    var refreshCalls = 0;
    final adapter = _FakeAdapter((opts) async {
      if (opts.path.endsWith('/auth/refresh')) {
        refreshCalls++;
        // Add a small delay so the two requests both hit the in-flight
        // gate before the refresh resolves.
        await Future<void>.delayed(const Duration(milliseconds: 20));
        return _json(
          200,
          '{"token":"new_access","refresh_token":"new_refresh"}',
        );
      }
      // Replay always succeeds.
      if (opts.extra['__retry'] == true) return _json(200, '{"ok":true}');
      return _json(401, '{"detail":"expired"}');
    });

    final container = _container(storage);
    addTearDown(container.dispose);
    final dio = container.read(dioProvider)..httpClientAdapter = adapter;

    final results = await Future.wait([
      dio.get<dynamic>('/api/v1/events'),
      dio.get<dynamic>('/api/v1/people'),
    ]);
    expect(results.every((r) => r.statusCode == 200), isTrue);
    expect(refreshCalls, 1, reason: 'concurrent 401s should share one refresh');
    expect(await storage.readToken(), 'new_access');
  });
}
