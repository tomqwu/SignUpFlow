// Wraps flutter_secure_storage so the rest of the app can swap to an
// in-memory mock for tests without depending on native plugin channels.

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

abstract class SecureTokenStorage {
  Future<String?> readToken();
  Future<void> writeToken(String token);
  Future<void> clearToken();
}

class _RealStorage implements SecureTokenStorage {
  static const _key = 'signupflow.jwt';
  final _impl = const FlutterSecureStorage(
    iOptions: IOSOptions(accessibility: KeychainAccessibility.first_unlock),
  );

  @override
  Future<String?> readToken() => _impl.read(key: _key);

  @override
  Future<void> writeToken(String token) =>
      _impl.write(key: _key, value: token);

  @override
  Future<void> clearToken() => _impl.delete(key: _key);
}

/// In-memory implementation used by tests via Riverpod overrides.
class InMemoryTokenStorage implements SecureTokenStorage {
  String? _token;

  @override
  Future<String?> readToken() async => _token;

  @override
  Future<void> writeToken(String token) async => _token = token;

  @override
  Future<void> clearToken() async => _token = null;
}

final secureTokenStorageProvider = Provider<SecureTokenStorage>((ref) {
  return _RealStorage();
});
