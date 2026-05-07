// Invitation accept screen — verifies the token (?token=...), shows the
// invitation preview (org, role, inviter), and lets the user set a
// password to claim the account.

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:signupflow_mobile/auth/auth_provider.dart';
import 'package:signupflow_mobile/auth/invitation_repository.dart';
import 'package:signupflow_mobile/shared/widgets/brand.dart';
import 'package:signupflow_mobile/shared/widgets/labeled_field.dart';
import 'package:signupflow_mobile/theme/colors.dart';
import 'package:signupflow_mobile/theme/components.dart';
import 'package:signupflow_mobile/theme/typography.dart';

class InvitationScreen extends ConsumerStatefulWidget {
  const InvitationScreen({required this.token, super.key});

  /// Token from the deep-link query param (`?token=...`). Empty string
  /// when the user navigates here without one — we show a paste form.
  final String token;

  @override
  ConsumerState<InvitationScreen> createState() => _InvitationScreenState();
}

class _InvitationScreenState extends ConsumerState<InvitationScreen> {
  final _password = TextEditingController();
  final _pasteToken = TextEditingController();
  Future<InvitationPreview>? _preview;
  bool _busy = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    if (widget.token.isNotEmpty) {
      _preview = ref.read(invitationRepositoryProvider).verify(widget.token);
    }
  }

  @override
  void didUpdateWidget(InvitationScreen old) {
    super.didUpdateWidget(old);
    if (old.token != widget.token && widget.token.isNotEmpty) {
      setState(() {
        _preview =
            ref.read(invitationRepositoryProvider).verify(widget.token);
      });
    }
  }

  @override
  void dispose() {
    _password.dispose();
    _pasteToken.dispose();
    super.dispose();
  }

  Future<void> _accept(InvitationPreview preview) async {
    if (_busy) return;
    final pw = _password.text;
    if (pw.length < 6) {
      setState(() => _error = 'Password must be at least 6 characters.');
      return;
    }
    setState(() {
      _busy = true;
      _error = null;
    });
    final err = await ref.read(authProvider.notifier).acceptInvitation(
          token: preview.token,
          password: pw,
        );
    if (!mounted) return;
    setState(() => _busy = false);
    if (err != null) {
      setState(() => _error = err);
      return;
    }
    final role = ref.read(authProvider).role;
    if (role == AuthRole.admin) {
      context.go('/a/dashboard');
    } else {
      context.go('/v/schedule');
    }
  }

  void _submitPastedToken() {
    final t = _pasteToken.text.trim();
    if (t.isEmpty) {
      setState(() => _error = 'Paste your invitation token to continue.');
      return;
    }
    context.go('/invitation?token=$t');
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
                  'ACCEPT INVITATION',
                  style: BlockType.monoTiny.copyWith(fontSize: 10),
                ),
                const SizedBox(height: 24),
                if (widget.token.isEmpty)
                  _PasteTokenForm(
                    controller: _pasteToken,
                    error: _error,
                    onSubmit: _submitPastedToken,
                  )
                else
                  FutureBuilder<InvitationPreview>(
                    future: _preview,
                    builder: (context, snap) {
                      if (snap.connectionState == ConnectionState.waiting) {
                        return const Padding(
                          padding: EdgeInsets.symmetric(vertical: 32),
                          child: Center(child: CircularProgressIndicator()),
                        );
                      }
                      if (snap.hasError) {
                        return _InvitationError(
                          message: snap.error.toString(),
                        );
                      }
                      final preview = snap.data!;
                      return _AcceptForm(
                        preview: preview,
                        password: _password,
                        busy: _busy,
                        error: _error,
                        onAccept: () => _accept(preview),
                      );
                    },
                  ),
                const SizedBox(height: 32),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _PasteTokenForm extends StatelessWidget {
  const _PasteTokenForm({
    required this.controller,
    required this.error,
    required this.onSubmit,
  });
  final TextEditingController controller;
  final String? error;
  final VoidCallback onSubmit;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        BlockCard(
          padding: const EdgeInsets.all(14),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('NO TOKEN IN LINK', style: BlockType.monoLabel),
              const SizedBox(height: 6),
              Text(
                'Paste the invitation token from your email below.',
                style: BlockType.bodySm.copyWith(color: BlockColors.ink2),
              ),
            ],
          ),
        ),
        const SizedBox(height: 12),
        LabeledField(
          label: 'Invitation token',
          controller: controller,
          hint: 'inv_…',
        ),
        if (error != null) ...[
          const SizedBox(height: 12),
          Text(
            error!,
            style: BlockType.bodySm.copyWith(color: BlockColors.danger),
            textAlign: TextAlign.center,
          ),
        ],
        const SizedBox(height: 18),
        BlockButton(label: 'Continue', onPressed: onSubmit),
      ],
    );
  }
}

class _AcceptForm extends StatelessWidget {
  const _AcceptForm({
    required this.preview,
    required this.password,
    required this.busy,
    required this.error,
    required this.onAccept,
  });
  final InvitationPreview preview;
  final TextEditingController password;
  final bool busy;
  final String? error;
  final VoidCallback onAccept;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        BlockCard(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('YOU ARE INVITED', style: BlockType.monoLabel),
              const SizedBox(height: 8),
              Text(
                preview.invitedName,
                style: BlockType.body.copyWith(fontWeight: FontWeight.w600),
              ),
              Text(
                preview.invitedEmail,
                style: BlockType.bodySm.copyWith(color: BlockColors.ink2),
              ),
              const SizedBox(height: 12),
              _row('Organization', preview.orgId),
              _row(
                'Role${preview.roles.length == 1 ? '' : 's'}',
                preview.roles.join(', '),
              ),
              _row('Invited by', preview.invitedBy),
            ],
          ),
        ),
        const SizedBox(height: 18),
        LabeledField(
          label: 'Choose a password',
          controller: password,
          hint: 'min 6 characters',
          obscure: true,
        ),
        if (error != null) ...[
          const SizedBox(height: 12),
          Text(
            error!,
            style: BlockType.bodySm.copyWith(color: BlockColors.danger),
            textAlign: TextAlign.center,
          ),
        ],
        const SizedBox(height: 18),
        BlockButton(
          label: busy ? 'Accepting…' : 'Accept invitation',
          onPressed: busy ? null : onAccept,
        ),
      ],
    );
  }

  Widget _row(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 110,
            child: Text(
              label.toUpperCase(),
              style: BlockType.monoLabel.copyWith(fontSize: 10),
            ),
          ),
          Expanded(child: Text(value, style: BlockType.bodySm)),
        ],
      ),
    );
  }
}

class _InvitationError extends StatelessWidget {
  const _InvitationError({required this.message});
  final String message;

  @override
  Widget build(BuildContext context) {
    return BlockCard(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('INVITATION ERROR', style: BlockType.monoLabel),
          const SizedBox(height: 8),
          Text(
            message,
            style: BlockType.body.copyWith(color: BlockColors.danger),
          ),
          const SizedBox(height: 14),
          Text(
            'Ask your admin to resend the invitation, or paste the token '
            'manually below.',
            style: BlockType.bodySm.copyWith(color: BlockColors.ink2),
          ),
        ],
      ),
    );
  }
}
