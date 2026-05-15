// Reset-password screen — takes ?token=... from a deep-link or paste,
// asks for a new password, calls POST /auth/reset-password, routes
// back to /login on success.

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:signupflow_mobile/auth/password_reset_repository.dart';
import 'package:signupflow_mobile/shared/widgets/brand.dart';
import 'package:signupflow_mobile/shared/widgets/labeled_field.dart';
import 'package:signupflow_mobile/theme/colors.dart';
import 'package:signupflow_mobile/theme/components.dart';
import 'package:signupflow_mobile/theme/typography.dart';

class ResetPasswordScreen extends ConsumerStatefulWidget {
  const ResetPasswordScreen({required this.token, super.key});

  /// Token from the deep-link query param. Empty string when the user
  /// navigates here without one — we show a paste form.
  final String token;

  @override
  ConsumerState<ResetPasswordScreen> createState() =>
      _ResetPasswordScreenState();
}

class _ResetPasswordScreenState extends ConsumerState<ResetPasswordScreen> {
  final _password = TextEditingController();
  final _confirm = TextEditingController();
  final _pasteToken = TextEditingController();
  bool _busy = false;
  bool _done = false;
  String? _error;

  @override
  void dispose() {
    _password.dispose();
    _confirm.dispose();
    _pasteToken.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (_busy) return;
    final token = widget.token.isNotEmpty
        ? widget.token
        : _pasteToken.text.trim();
    if (token.isEmpty) {
      setState(() => _error = 'Paste your reset token to continue.');
      return;
    }
    final pw = _password.text;
    if (pw.length < 6) {
      setState(() => _error = 'Password must be at least 6 characters.');
      return;
    }
    if (pw != _confirm.text) {
      setState(() => _error = "Passwords don't match.");
      return;
    }
    setState(() {
      _busy = true;
      _error = null;
    });
    try {
      await ref.read(passwordResetRepositoryProvider).confirmReset(
            token: token,
            newPassword: pw,
          );
      if (!mounted) return;
      setState(() {
        _busy = false;
        _done = true;
      });
    } on PasswordResetFailure catch (e) {
      if (!mounted) return;
      setState(() {
        _busy = false;
        _error = e.message;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 28),
          child: SingleChildScrollView(
            child: Column(
              children: [
                const SizedBox(height: 28),
                Align(
                  alignment: Alignment.centerLeft,
                  child: TextButton(
                    onPressed: () => context.go('/login'),
                    style: TextButton.styleFrom(
                      foregroundColor: BlockColors.ink2,
                      padding: EdgeInsets.zero,
                      minimumSize: const Size(0, 24),
                      tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                    ),
                    child: Text(
                      '← Back to sign in',
                      style: BlockType.bodySm.copyWith(
                        color: context.blockColor(
                          light: BlockColors.ink2,
                          dark: BlockColors.ink2Dark,
                        ),
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 12),
                const BrandMark(size: 56),
                const SizedBox(height: 14),
                const Wordmark(size: 22),
                const SizedBox(height: 8),
                Text(
                  'SET NEW PASSWORD',
                  style: BlockType.monoTiny.copyWith(fontSize: 10),
                ),
                const SizedBox(height: 24),
                if (_done)
                  _DoneCard(onContinue: () => context.go('/login'))
                else ...[
                  if (widget.token.isEmpty) ...[
                    LabeledField(
                      label: 'Reset token',
                      controller: _pasteToken,
                      hint: 'rst_…',
                    ),
                    const SizedBox(height: 10),
                  ],
                  LabeledField(
                    label: 'New password',
                    controller: _password,
                    hint: 'min 6 characters',
                    obscure: true,
                  ),
                  const SizedBox(height: 10),
                  LabeledField(
                    label: 'Confirm password',
                    controller: _confirm,
                    hint: 'retype password',
                    obscure: true,
                  ),
                  if (_error != null) ...[
                    const SizedBox(height: 12),
                    Text(
                      _error!,
                      style: BlockType.bodySm
                          .copyWith(color: BlockColors.danger),
                      textAlign: TextAlign.center,
                    ),
                  ],
                  const SizedBox(height: 18),
                  BlockButton(
                    label: _busy ? 'Resetting…' : 'Reset password',
                    onPressed: _busy ? null : _submit,
                  ),
                ],
                const SizedBox(height: 32),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _DoneCard extends StatelessWidget {
  const _DoneCard({required this.onContinue});
  final VoidCallback onContinue;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        BlockCard(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('PASSWORD RESET', style: BlockType.monoLabel),
              const SizedBox(height: 8),
              Text(
                'You can now sign in with your new password.',
                style: BlockType.body,
              ),
            ],
          ),
        ),
        const SizedBox(height: 18),
        BlockButton(label: 'Sign in', onPressed: onContinue),
      ],
    );
  }
}
