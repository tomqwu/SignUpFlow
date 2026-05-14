import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:signupflow_mobile/routing/router.dart';
import 'package:signupflow_mobile/theme/theme.dart';
import 'package:signupflow_mobile/theme/theme_provider.dart';

class SignUpFlowApp extends ConsumerWidget {
  const SignUpFlowApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // While the persisted theme mode hydrates, fall back to ThemeMode.system
    // so we don't flash the wrong theme on cold start.
    final themeMode =
        ref.watch(themeModeProvider).valueOrNull ?? ThemeMode.system;
    return MaterialApp.router(
      title: 'SignUpFlow',
      theme: buildBlockMonoTheme(),
      darkTheme: buildBlockMonoDarkTheme(),
      themeMode: themeMode,
      debugShowCheckedModeBanner: false,
      routerConfig: buildRouter(ref),
    );
  }
}
