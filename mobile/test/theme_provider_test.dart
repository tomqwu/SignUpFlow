// Sprint 10 PR 10.4 — theme_provider unit tests.
//
// Pins the persistence contract: changes round-trip to storage; cold
// start hydrates from the persisted value; unknown / missing values
// default to ThemeMode.system.

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:signupflow_mobile/theme/theme_provider.dart';

ProviderContainer _container(InMemoryThemeModeStorage storage) {
  return ProviderContainer(
    overrides: [
      themeModeStorageProvider.overrideWithValue(storage),
    ],
  );
}

void main() {
  test('initial state is ThemeMode.system when storage is empty', () async {
    final storage = InMemoryThemeModeStorage();
    final container = _container(storage);
    addTearDown(container.dispose);

    final mode = await container.read(themeModeProvider.future);
    expect(mode, ThemeMode.system);
  });

  test('initial state hydrates from persisted value', () async {
    final storage = InMemoryThemeModeStorage();
    await storage.write('dark');
    final container = _container(storage);
    addTearDown(container.dispose);

    final mode = await container.read(themeModeProvider.future);
    expect(mode, ThemeMode.dark);
  });

  test('set() updates state and persists to storage', () async {
    final storage = InMemoryThemeModeStorage();
    final container = _container(storage);
    addTearDown(container.dispose);

    // Wait for the initial async load to settle.
    await container.read(themeModeProvider.future);

    await container.read(themeModeProvider.notifier).set(ThemeMode.dark);

    expect(container.read(themeModeProvider).valueOrNull, ThemeMode.dark);
    expect(await storage.read(), 'dark');
  });

  test('unknown stored value falls back to ThemeMode.system', () async {
    final storage = InMemoryThemeModeStorage();
    await storage.write('not-a-mode');
    final container = _container(storage);
    addTearDown(container.dispose);

    final mode = await container.read(themeModeProvider.future);
    expect(mode, ThemeMode.system);
  });

  test('persisted value survives container recreation', () async {
    final storage = InMemoryThemeModeStorage();
    final container1 = _container(storage);
    await container1.read(themeModeProvider.future);
    await container1.read(themeModeProvider.notifier).set(ThemeMode.light);
    container1.dispose();

    // New container reads from the same backing storage.
    final container2 = _container(storage);
    addTearDown(container2.dispose);
    final mode = await container2.read(themeModeProvider.future);
    expect(mode, ThemeMode.light);
  });
}
