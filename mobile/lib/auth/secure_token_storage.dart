// Wraps flutter_secure_storage so the rest of the app can swap to an
// in-memory mock for tests without depending on native plugin channels.

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

abstract class SecureTokenStorage {
  // Access token (Authorization: Bearer ...)
  Future<String?> readToken();
  Future<void> writeToken(String token);
  Future<void> clearToken();

  // Long-lived refresh token used by /auth/refresh.
  Future<String?> readRefreshToken();
  Future<void> writeRefreshToken(String token);
  Future<void> clearRefreshToken();

  /// Convenience: nukes both tokens. Used on logout and on a 401 that
  /// can't be recovered via /auth/refresh.
  Future<void> clearAll();

  /// Monotonic counter bumped on every write/clear. The refresh
  /// interceptor captures this at request time and verifies it hasn't
  /// changed before persisting response tokens. If it has — signOut(),
  /// a fresh login, or another refresh response landed in between —
  /// the response is dropped without mutating storage. Closes the
  /// TOCTOU window in `readRefreshToken() → compare → writeToken()`.
  int get sessionGeneration;

  /// Atomic compare-and-set: if `sessionGeneration == expectedGen`,
  /// bump the generation and persist both tokens; otherwise return
  /// false without mutating state.
  ///
  /// The gen check + bump + write are kept in a single async function
  /// so the synchronous prelude (check + claim generation) runs to
  /// completion before any awaitable yield, preventing the
  /// "another mutator passes the check before we increment" race
  /// inherent in the old gen-check-then-two-separate-writes shape.
  ///
  /// Residual race: in `_RealStorage`, between the two platform writes
  /// another mutator can still interleave. By the time the second
  /// write completes the "current" storage is the merged result of
  /// whichever calls landed last. That's a platform-call-latency
  /// window only; closing it fully needs `package:synchronized` or
  /// a platform-side atomic write API.
  Future<bool> compareAndWriteTokens({
    required int expectedGen,
    required String access,
    required String refresh,
  });
}

class _RealStorage implements SecureTokenStorage {
  static const _accessKey = 'signupflow.jwt';
  static const _refreshKey = 'signupflow.refresh_jwt';
  final _impl = const FlutterSecureStorage(
    iOptions: IOSOptions(accessibility: KeychainAccessibility.first_unlock),
  );
  int _gen = 0;

  @override
  int get sessionGeneration => _gen;

  @override
  Future<String?> readToken() => _impl.read(key: _accessKey);

  @override
  Future<void> writeToken(String token) async {
    _gen++;
    await _impl.write(key: _accessKey, value: token);
  }

  @override
  Future<void> clearToken() async {
    _gen++;
    await _impl.delete(key: _accessKey);
  }

  @override
  Future<String?> readRefreshToken() => _impl.read(key: _refreshKey);

  @override
  Future<void> writeRefreshToken(String token) async {
    _gen++;
    await _impl.write(key: _refreshKey, value: token);
  }

  @override
  Future<void> clearRefreshToken() async {
    _gen++;
    await _impl.delete(key: _refreshKey);
  }

  @override
  Future<void> clearAll() async {
    _gen++;
    await _impl.delete(key: _accessKey);
    await _impl.delete(key: _refreshKey);
  }

  @override
  Future<bool> compareAndWriteTokens({
    required int expectedGen,
    required String access,
    required String refresh,
  }) async {
    // Synchronous prelude — runs to completion before any await.
    // Once `_gen != expectedGen`, the caller's view of the world is
    // stale; reject. Otherwise claim the new generation atomically.
    if (_gen != expectedGen) {
      return false;
    }
    _gen++;
    // The two awaited platform writes can interleave with other
    // mutators, but the gen has already advanced, so any concurrent
    // gen-check will see the bumped value and reject. Final stored
    // value depends on write completion order — that's the
    // documented narrow window.
    await _impl.write(key: _accessKey, value: access);
    await _impl.write(key: _refreshKey, value: refresh);
    return true;
  }
}

/// In-memory implementation used by tests via Riverpod overrides.
class InMemoryTokenStorage implements SecureTokenStorage {
  String? _token;
  String? _refresh;
  int _gen = 0;

  @override
  int get sessionGeneration => _gen;

  @override
  Future<String?> readToken() async => _token;

  @override
  Future<void> writeToken(String token) async {
    _gen++;
    _token = token;
  }

  @override
  Future<void> clearToken() async {
    _gen++;
    _token = null;
  }

  @override
  Future<String?> readRefreshToken() async => _refresh;

  @override
  Future<void> writeRefreshToken(String token) async {
    _gen++;
    _refresh = token;
  }

  @override
  Future<void> clearRefreshToken() async {
    _gen++;
    _refresh = null;
  }

  @override
  Future<void> clearAll() async {
    _gen++;
    _token = null;
    _refresh = null;
  }

  @override
  Future<bool> compareAndWriteTokens({
    required int expectedGen,
    required String access,
    required String refresh,
  }) async {
    // Trivially atomic in the in-memory case — no awaits at all once
    // we're past the synchronous prelude (Dart `async` functions
    // execute to first await synchronously; without any await here,
    // the whole body runs as a single microtask).
    if (_gen != expectedGen) {
      return false;
    }
    _gen++;
    _token = access;
    _refresh = refresh;
    return true;
  }
}

final secureTokenStorageProvider = Provider<SecureTokenStorage>((ref) {
  return _RealStorage();
});
