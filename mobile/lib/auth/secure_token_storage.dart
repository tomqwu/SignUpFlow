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
}

class _RealStorage implements SecureTokenStorage {
  static const _accessKey = 'signupflow.jwt';
  static const _refreshKey = 'signupflow.refresh_jwt';
  final _impl = const FlutterSecureStorage(
    iOptions: IOSOptions(accessibility: KeychainAccessibility.first_unlock),
  );

  @override
  Future<String?> readToken() => _impl.read(key: _accessKey);

  @override
  Future<void> writeToken(String token) => _impl.write(key: _accessKey, value: token);

  @override
  Future<void> clearToken() => _impl.delete(key: _accessKey);

  @override
  Future<String?> readRefreshToken() => _impl.read(key: _refreshKey);

  @override
  Future<void> writeRefreshToken(String token) => _impl.write(key: _refreshKey, value: token);

  @override
  Future<void> clearRefreshToken() => _impl.delete(key: _refreshKey);

  @override
  Future<void> clearAll() async {
    await _impl.delete(key: _accessKey);
    await _impl.delete(key: _refreshKey);
  }
}

/// In-memory implementation used by tests via Riverpod overrides.
class InMemoryTokenStorage implements SecureTokenStorage {
  String? _token;
  String? _refresh;

  @override
  Future<String?> readToken() async => _token;

  @override
  Future<void> writeToken(String token) async => _token = token;

  @override
  Future<void> clearToken() async => _token = null;

  @override
  Future<String?> readRefreshToken() async => _refresh;

  @override
  Future<void> writeRefreshToken(String token) async => _refresh = token;

  @override
  Future<void> clearRefreshToken() async => _refresh = null;

  @override
  Future<void> clearAll() async {
    _token = null;
    _refresh = null;
  }
}

final secureTokenStorageProvider = Provider<SecureTokenStorage>((ref) {
  return _RealStorage();
});
