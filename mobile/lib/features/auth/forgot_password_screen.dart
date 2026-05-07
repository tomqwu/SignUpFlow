// Forgot-password screen — email field → POST /auth/forgot-password
// → confirmation message. The backend deliberately returns the same
// generic response regardless of whether the email exists
// (anti-enumeration), so the UI mirrors that.

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:signupflow_mobile/auth/password_reset_repository.dart';
import 'package:signupflow_mobile/shared/widgets/brand.dart';
import 'package:signupflow_mobile/shared/widgets/labeled_field.dart';
import 'package:signupflow_mobile/theme/colors.dart';
import 'package:signupflow_mobile/theme/components.dart';
import 'package:signupflow_mobile/theme/typography.dart';

class ForgotPasswordScreen extends ConsumerStatefulWidget {
  const ForgotPasswordScreen({super.key});

  @override
  ConsumerState<ForgotPasswordScreen> createState() =>
      _ForgotPasswordScreenState();
}

class _ForgotPasswordScreenState extends ConsumerState<ForgotPasswordScreen> {
  final _email = TextEditingController();
  bool _busy = false;
  bool _submitted = false;
  String? _error;

  @override
  void dispose() {
    _email.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (_busy) return;
    final email = _email.text.trim();
    if (email.isEmpty) {
      setState(() => _error = 'Email required.');
      return;
    }
    setState(() {
      _busy = true;
      _error = null;
    });
    try {
      await ref
          .read(passwordResetRepositoryProvider)
          .requestReset(email);
      if (!mounted) return;
      setState(() {
        _busy = false;
        _submitted = true;
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
                      style: BlockType.bodySm
                          .copyWith(color: BlockColors.ink2),
                    ),
                  ),
                ),
                const SizedBox(height: 12),
                const BrandMark(size: 56),
                const SizedBox(height: 14),
                const Wordmark(size: 22),
                const SizedBox(height: 8),
                Text(
                  'RESET PASSWORD',
                  style: BlockType.monoTiny.copyWith(fontSize: 10),
                ),
                const SizedBox(height: 28),
                if (_submitted)
                  _SubmittedCard(email: _email.text.trim())
                else ...[
                  LabeledField(
                    label: 'Email',
                    controller: _email,
                    hint: 'you@church.org',
                    keyboard: TextInputType.emailAddress,
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
                    label: _busy ? 'Sending…' : 'Send reset link',
                    onPressed: _busy ? null : _submit,
                  ),
                  const SizedBox(height: 16),
                  Text(
                    "We'll email you a reset link if your address has an "
                    'account.',
                    textAlign: TextAlign.center,
                    style: BlockType.bodySm
                        .copyWith(color: BlockColors.ink3),
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

class _SubmittedCard extends StatelessWidget {
  const _SubmittedCard({required this.email});
  final String email;

  @override
  Widget build(BuildContext context) {
    return BlockCard(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('CHECK YOUR EMAIL', style: BlockType.monoLabel),
          const SizedBox(height: 8),
          Text(
            "If $email is registered with us, you'll receive a reset "
            'link shortly. Open the link on this device — it will bring '
            'you back here to set a new password.',
            style: BlockType.bodySm,
          ),
          const SizedBox(height: 14),
          Text(
            "Didn't get an email? Check your spam folder or try again.",
            style: BlockType.bodySm.copyWith(color: BlockColors.ink2),
          ),
        ],
      ),
    );
  }
}
