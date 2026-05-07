import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:signupflow_mobile/routing/router.dart';
import 'package:signupflow_mobile/theme/theme.dart';

class SignUpFlowApp extends ConsumerWidget {
  const SignUpFlowApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return MaterialApp.router(
      title: 'SignUpFlow',
      theme: buildBlockMonoTheme(),
      debugShowCheckedModeBanner: false,
      routerConfig: buildRouter(ref),
    );
  }
}
