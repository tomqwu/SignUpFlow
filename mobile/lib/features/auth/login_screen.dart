// Login screen — wired to /auth/login + flutter_secure_storage in PR 7.2.
// Visual matches mobile/prototype/screenshots/v2/01-login.png.
// Demo shortcuts retained — they bypass the network for offline dev.

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:signupflow_mobile/auth/auth_provider.dart';
import 'package:signupflow_mobile/shared/widgets/brand.dart';
import 'package:signupflow_mobile/theme/colors.dart';
import 'package:signupflow_mobile/theme/components.dart';
import 'package:signupflow_mobile/theme/typography.dart';

class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({super.key});

  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen> {
  final _email = TextEditingController();
  final _password = TextEditingController();
  bool _busy = false;
  String? _error;

  @override
  void dispose() {
    _email.dispose();
    _password.dispose();
    super.dispose();
  }

  Future<void> _signIn() async {
    if (_busy) return;
    final email = _email.text.trim();
    final pw = _password.text;
    if (email.isEmpty || pw.isEmpty) {
      setState(() => _error = 'Email and password required');
      return;
    }
    setState(() {
      _busy = true;
      _error = null;
    });
    final err = await ref.read(authProvider.notifier).signIn(email, pw);
    if (!mounted) return;
    setState(() => _busy = false);
    if (err != null) {
      setState(() => _error = err);
      return;
    }
    final role = ref.read(authProvider).role;
    if (role == AuthRole.admin) {
      context.go('/a/dashboard');
    } else if (role == AuthRole.volunteer) {
      context.go('/v/schedule');
    } else {
      setState(() => _error = 'No role assigned. Contact your admin.');
    }
  }

  @override
  Widget build(BuildContext context) {
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

                _Field(
                  label: 'Email',
                  controller: _email,
                  hint: 'you@church.org',
                  keyboard: TextInputType.emailAddress,
                ),
                const SizedBox(height: 10),
                _Field(
                  label: 'Password',
                  controller: _password,
                  hint: '•••••••',
                  obscure: true,
                ),

                if (_error != null) ...[
                  const SizedBox(height: 12),
                  Text(
                    _error!,
                    style: BlockType.bodySm.copyWith(color: BlockColors.danger),
                    textAlign: TextAlign.center,
                  ),
                ],

                const SizedBox(height: 18),
                BlockButton(
                  label: _busy ? 'Signing in…' : 'Sign in',
                  onPressed: _busy ? null : _signIn,
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
    required this.controller,
    required this.hint,
    this.obscure = false,
    this.keyboard,
  });

  final String label;
  final TextEditingController controller;
  final String hint;
  final bool obscure;
  final TextInputType? keyboard;

  @override
  Widget build(BuildContext context) {
    return BlockCard(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            label.toUpperCase(),
            style: BlockType.monoLabel.copyWith(fontSize: 10),
          ),
          TextField(
            controller: controller,
            obscureText: obscure,
            keyboardType: keyboard,
            autocorrect: false,
            enableSuggestions: !obscure,
            style: BlockType.body,
            decoration: InputDecoration(
              hintText: hint,
              hintStyle: BlockType.body.copyWith(color: BlockColors.ink3),
              border: InputBorder.none,
              isDense: true,
              contentPadding: EdgeInsets.zero,
            ),
          ),
        ],
      ),
    );
  }
}
