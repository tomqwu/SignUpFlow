import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import 'package:signupflow_mobile/auth/auth_provider.dart';
import 'package:signupflow_mobile/shared/widgets/stub_screen.dart';
import 'package:signupflow_mobile/theme/components.dart';

class VolunteerProfileScreen extends ConsumerWidget {
  const VolunteerProfileScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      body: SafeArea(
        child: Stack(
          children: [
            const StubScreen(
              title: 'Profile',
              endpoint: 'GET /people/me · POST /calendar/reset',
              willLandIn: 'PR 7.6',
            ),
            Positioned(
              left: 16,
              right: 16,
              bottom: 16,
              child: BlockButton(
                label: 'Log out',
                kind: BlockButtonKind.destructive,
                onPressed: () {
                  ref.read(authProvider.notifier).signOut();
                  context.go('/login');
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}
