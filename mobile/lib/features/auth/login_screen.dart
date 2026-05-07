// Login screen — Sprint 7.1 stub. Real /auth/login wiring lands in 7.2.
// Visual: matches mobile/prototype/screenshots/v2/01-login.png.

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import 'package:signupflow_mobile/auth/auth_provider.dart';
import 'package:signupflow_mobile/shared/widgets/brand.dart';
import 'package:signupflow_mobile/theme/colors.dart';
import 'package:signupflow_mobile/theme/components.dart';
import 'package:signupflow_mobile/theme/typography.dart';

class LoginScreen extends ConsumerWidget {
  const LoginScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final auth = ref.read(authProvider.notifier);

    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 28),
          child: SingleChildScrollView(
            child: Column(
              children: [
                const SizedBox(height: 48),
                const BrandMark(size: 72),
                const SizedBox(height: 22),
                const Wordmark(size: 24),
                const SizedBox(height: 8),
                Text(
                  'VOLUNTEER SCHEDULING · v1.0',
                  style: BlockType.monoTiny.copyWith(fontSize: 10),
                ),
                const SizedBox(height: 44),

                const _Field(label: 'Email', placeholder: 'you@church.org'),
                const SizedBox(height: 10),
                const _Field(
                  label: 'Password',
                  placeholder: '•••••••',
                  obscure: true,
                ),

                const SizedBox(height: 18),
                BlockButton(
                  label: 'Sign in',
                  onPressed: () =>
                      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
                    content: Text('Real /auth/login lands in PR 7.2'),
                  )),
                ),
                const SizedBox(height: 20),
                Text(
                  '· Forgot password? ·',
                  style: BlockType.bodySm.copyWith(color: BlockColors.ink2),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 36),

                BlockCard(
                  padding: const EdgeInsets.all(14),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Text('DEMO SHORTCUT', style: BlockType.monoLabel),
                      const SizedBox(height: 8),
                      Row(
                        children: [
                          Expanded(
                            child: BlockButton(
                              label: 'Volunteer',
                              kind: BlockButtonKind.secondary,
                              onPressed: () {
                                auth.demoSignInVolunteer();
                                context.go('/v/schedule');
                              },
                            ),
                          ),
                          const SizedBox(width: 8),
                          Expanded(
                            child: BlockButton(
                              label: 'Admin',
                              kind: BlockButtonKind.secondary,
                              onPressed: () {
                                auth.demoSignInAdmin();
                                context.go('/a/dashboard');
                              },
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 24),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _Field extends StatelessWidget {
  const _Field({
    required this.label,
    required this.placeholder,
    this.obscure = false,
  });

  final String label;
  final String placeholder;
  final bool obscure;

  @override
  Widget build(BuildContext context) {
    return BlockCard(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label.toUpperCase(), style: BlockType.monoLabel.copyWith(fontSize: 10)),
          const SizedBox(height: 4),
          Text(
            placeholder,
            style: BlockType.body.copyWith(
              color: BlockColors.ink3,
              letterSpacing: obscure ? 6 : 0,
            ),
          ),
        ],
      ),
    );
  }
}
