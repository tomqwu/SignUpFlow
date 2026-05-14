// Sprint 10 PR 10.4 — Riverpod-driven theme mode (system / light / dark)
// with persistence via flutter_secure_storage (the same backing store
// SecureTokenStorage uses — no new dep).
//
// The provider is async-initialized: on first app launch we read the
// persisted value (or fall back to ThemeMode.system if absent), and
// emit it via the AsyncValue API. MaterialApp.router consumes the
// current value via `ref.watch(themeModeProvider)`.

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

/// Storage key — namespaced under signupflow. flutter_secure_storage
/// shares the iOS Keychain / Android Keystore that SecureTokenStorage
/// uses, so this key lives next to signupflow.jwt / signupflow.refresh_jwt.
const _themeModeKey = 'signupflow.theme_mode';

/// Encodes [ThemeMode] to / from a stable string. Stored values:
/// "system" / "light" / "dark". Unknown / null → defaults to system.
String _encode(ThemeMode mode) => switch (mode) {
      ThemeMode.system => 'system',
      ThemeMode.light => 'light',
      ThemeMode.dark => 'dark',
    };

ThemeMode _decode(String? raw) => switch (raw) {
      'light' => ThemeMode.light,
      'dark' => ThemeMode.dark,
      _ => ThemeMode.system,
    };

/// Abstraction over flutter_secure_storage so tests can inject an
/// in-memory backing store without a platform channel.
abstract class ThemeModeStorage {
  Future<String?> read();
  Future<void> write(String value);
}

class _SecureThemeModeStorage implements ThemeModeStorage {
  static const _impl = FlutterSecureStorage(
    iOptions: IOSOptions(accessibility: KeychainAccessibility.first_unlock),
  );

  @override
  Future<String?> read() => _impl.read(key: _themeModeKey);

  @override
  Future<void> write(String value) =>
      _impl.write(key: _themeModeKey, value: value);
}

/// In-memory implementation for tests via Riverpod overrides.
class InMemoryThemeModeStorage implements ThemeModeStorage {
  String? _value;

  @override
  Future<String?> read() async => _value;

  @override
  Future<void> write(String value) async {
    _value = value;
  }
}

final themeModeStorageProvider = Provider<ThemeModeStorage>(
  (ref) => _SecureThemeModeStorage(),
);

/// Notifier for the active [ThemeMode]. Initial state hydrates from
/// persistent storage; updates write through.
class ThemeModeNotifier extends AsyncNotifier<ThemeMode> {
  @override
  Future<ThemeMode> build() async {
    final storage = ref.read(themeModeStorageProvider);
    final raw = await storage.read();
    return _decode(raw);
  }

  Future<void> set(ThemeMode mode) async {
    state = AsyncValue.data(mode);
    final storage = ref.read(themeModeStorageProvider);
    await storage.write(_encode(mode));
  }
}

final themeModeProvider = AsyncNotifierProvider<ThemeModeNotifier, ThemeMode>(
  ThemeModeNotifier.new,
);
