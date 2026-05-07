// Create-organization signup. First user in a new org becomes admin.

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:signupflow_mobile/auth/auth_provider.dart';
import 'package:signupflow_mobile/shared/widgets/brand.dart';
import 'package:signupflow_mobile/shared/widgets/labeled_field.dart';
import 'package:signupflow_mobile/theme/colors.dart';
import 'package:signupflow_mobile/theme/components.dart';
import 'package:signupflow_mobile/theme/typography.dart';

class CreateOrgScreen extends ConsumerStatefulWidget {
  const CreateOrgScreen({super.key});

  @override
  ConsumerState<CreateOrgScreen> createState() => _CreateOrgScreenState();
}

class _CreateOrgScreenState extends ConsumerState<CreateOrgScreen> {
  final _orgName = TextEditingController();
  final _orgId = TextEditingController();
  final _adminName = TextEditingController();
  final _email = TextEditingController();
  final _password = TextEditingController();
  bool _busy = false;
  String? _error;
  bool _slugManuallyEdited = false;

  @override
  void initState() {
    super.initState();
    _orgName.addListener(_maybeAutofillSlug);
    _orgId.addListener(_trackManualEdit);
  }

  @override
  void dispose() {
    _orgName.dispose();
    _orgId.dispose();
    _adminName.dispose();
    _email.dispose();
    _password.dispose();
    super.dispose();
  }

  void _maybeAutofillSlug() {
    if (_slugManuallyEdited) return;
    final auto = _slugify(_orgName.text);
    if (_orgId.text != auto) {
      // Setting via setText would re-trigger our own listener; bypass with a
      // direct assignment + selection-preserving update.
      _orgId.value = TextEditingValue(
        text: auto,
        selection: TextSelection.collapsed(offset: auto.length),
      );
    }
  }

  void _trackManualEdit() {
    final auto = _slugify(_orgName.text);
    if (_orgId.text != auto) _slugManuallyEdited = true;
    if (_orgId.text.isEmpty) _slugManuallyEdited = false;
  }

  static String _slugify(String name) {
    final lower = name.toLowerCase().trim();
    final cleaned = lower.replaceAll(RegExp('[^a-z0-9]+'), '-');
    // Trim leading/trailing dashes; need a literal dollar sign so the regex
    // anchors to end-of-string, hence the explicit string concat.
    return cleaned.replaceAll(RegExp('^-+|-+' r'$'), '');
  }

  Future<void> _submit() async {
    if (_busy) return;
    final orgName = _orgName.text.trim();
    final orgId = _orgId.text.trim();
    final adminName = _adminName.text.trim();
    final email = _email.text.trim();
    final pw = _password.text;

    if (orgName.isEmpty ||
        orgId.isEmpty ||
        adminName.isEmpty ||
        email.isEmpty ||
        pw.isEmpty) {
      setState(() => _error = 'All fields are required.');
      return;
    }
    if (pw.length < 6) {
      setState(() => _error = 'Password must be at least 6 characters.');
      return;
    }
    if (!RegExp(r'^[a-z0-9][a-z0-9-]*[a-z0-9]$').hasMatch(orgId)) {
      setState(() =>
          _error = 'Org ID must be lowercase letters, numbers, and dashes.');
      return;
    }

    setState(() {
      _busy = true;
      _error = null;
    });
    final err =
        await ref.read(authProvider.notifier).createOrgAndSignUp(
              orgId: orgId,
              orgName: orgName,
              adminName: adminName,
              email: email,
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
    } else if (role == AuthRole.volunteer) {
      context.go('/v/schedule');
    } else {
      setState(() => _error = 'No role assigned. Contact your admin.');
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
                  'CREATE A NEW ORGANIZATION',
                  style: BlockType.monoTiny.copyWith(fontSize: 10),
                ),
                const SizedBox(height: 28),

                LabeledField(
                  label: 'Organization name',
                  controller: _orgName,
                  hint: 'Hope Community Church',
                  textCapitalization: TextCapitalization.words,
                  autocorrect: true,
                ),
                const SizedBox(height: 10),
                LabeledField(
                  label: 'Org ID (used in URLs)',
                  controller: _orgId,
                  hint: 'hope-community',
                ),
                const SizedBox(height: 22),
                LabeledField(
                  label: 'Your name',
                  controller: _adminName,
                  hint: 'Pastor Sarah',
                  textCapitalization: TextCapitalization.words,
                ),
                const SizedBox(height: 10),
                LabeledField(
                  label: 'Email',
                  controller: _email,
                  hint: 'you@church.org',
                  keyboard: TextInputType.emailAddress,
                ),
                const SizedBox(height: 10),
                LabeledField(
                  label: 'Password',
                  controller: _password,
                  hint: 'min 6 characters',
                  obscure: true,
                ),

                if (_error != null) ...[
                  const SizedBox(height: 12),
                  Text(
                    _error!,
                    style:
                        BlockType.bodySm.copyWith(color: BlockColors.danger),
                    textAlign: TextAlign.center,
                  ),
                ],

                const SizedBox(height: 18),
                BlockButton(
                  label: _busy ? 'Creating…' : 'Create organization',
                  onPressed: _busy ? null : _submit,
                ),
                const SizedBox(height: 16),
                Text(
                  'You become the first admin of the new organization.',
                  textAlign: TextAlign.center,
                  style: BlockType.bodySm.copyWith(color: BlockColors.ink3),
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
