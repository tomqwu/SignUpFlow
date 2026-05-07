// Volunteer Profile — Sprint 7.6.
// Visual target: mobile/prototype/screenshots/v2/07-v-profile.png.
//
// Loads PersonResponse + CalendarSubscriptionResponse from profileProvider.
// Reset-token mutation invalidates the provider so the new ICS URL renders
// without a manual refresh. Log out wipes Riverpod state + secure storage
// then routes to /login.

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:signupflow_api/signupflow_api.dart' as api;
import 'package:signupflow_mobile/auth/auth_provider.dart';
import 'package:signupflow_mobile/features/volunteer/profile_provider.dart';
import 'package:signupflow_mobile/theme/colors.dart';
import 'package:signupflow_mobile/theme/components.dart';
import 'package:signupflow_mobile/theme/typography.dart';

class VolunteerProfileScreen extends ConsumerWidget {
  const VolunteerProfileScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final asyncData = ref.watch(profileProvider);
    return Scaffold(
      body: SafeArea(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const PageTitle('Profile'),
            Expanded(
              child: asyncData.when(
                loading: () => const Center(child: CircularProgressIndicator()),
                error: (e, _) => Center(
                  child: Padding(
                    padding: const EdgeInsets.all(24),
                    child: Text(
                      'Failed to load profile: $e',
                      style: BlockType.bodySm,
                      textAlign: TextAlign.center,
                    ),
                  ),
                ),
                data: (data) => _Body(data: data),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _Body extends ConsumerWidget {
  const _Body({required this.data});
  final ProfileData data;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final person = data.person;
    final email = person.email ?? '—';
    return SingleChildScrollView(
      padding: const EdgeInsets.fromLTRB(16, 0, 16, 96),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          BlockCard(
            child: Row(
              children: [
                AvatarBadge(name: person.name, size: 64),
                const SizedBox(width: 14),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        person.name,
                        style: BlockType.subhead.copyWith(fontSize: 18),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        email.toUpperCase(),
                        style: BlockType.monoTiny.copyWith(fontSize: 10),
                      ),
                      Text(
                        person.orgId.toUpperCase(),
                        style: BlockType.monoTiny.copyWith(
                          fontSize: 10,
                          color: BlockColors.accent,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          const MonoLabel('Calendar export'),
          if (data.subscription case final api.CalendarSubscriptionResponse sub)
            _CalendarCard(subscription: sub)
          else
            BlockCard(
              child: Text(
                'Calendar export unavailable — subscription URL is unset.',
                style: BlockType.bodySm,
              ),
            ),
          const MonoLabel('Settings'),
          _SettingRow(
            label: 'Language',
            value: _resolveLanguage(person.language ?? 'en'),
          ),
          _SettingRow(
            label: 'Time zone',
            value: person.timezone ?? 'UTC',
          ),
          _SettingRow(
            label: 'Roles',
            value: (person.roles?.toList() ?? const <String>[]).join(' · ').toUpperCase(),
          ),
          const SizedBox(height: 16),
          BlockButton(
            label: 'Log out',
            kind: BlockButtonKind.destructive,
            onPressed: () async {
              await ref.read(authProvider.notifier).signOut();
              if (!context.mounted) return;
              context.go('/login');
            },
          ),
        ],
      ),
    );
  }

  String _resolveLanguage(String code) {
    return switch (code.toLowerCase()) {
      'en' => 'English',
      'es' => 'Español',
      'fr' => 'Français',
      'de' => 'Deutsch',
      'pt' => 'Português',
      'zh' => '中文',
      _ => code.toUpperCase(),
    };
  }
}

class _CalendarCard extends ConsumerWidget {
  const _CalendarCard({required this.subscription});
  final api.CalendarSubscriptionResponse subscription;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final url = subscription.httpsUrl;
    final busy = ref.watch(profileMutationsProvider);
    return BlockCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
            decoration: BoxDecoration(
              color: BlockColors.accentSoft,
              borderRadius: BorderRadius.circular(6),
            ),
            child: Text(
              url.toUpperCase(),
              style: BlockType.monoData.copyWith(
                color: BlockColors.accentInk,
                fontSize: 11,
              ),
              softWrap: true,
            ),
          ),
          const SizedBox(height: 10),
          Row(
            children: [
              Expanded(
                child: BlockButton(
                  label: 'Copy URL',
                  kind: BlockButtonKind.secondary,
                  onPressed: () async {
                    await Clipboard.setData(ClipboardData(text: url));
                    if (!context.mounted) return;
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('Copied to clipboard')),
                    );
                  },
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: BlockButton(
                  label: busy ? 'Resetting…' : 'Reset token',
                  kind: BlockButtonKind.secondary,
                  onPressed: busy
                      ? null
                      : () async {
                          final err = await ref
                              .read(profileMutationsProvider.notifier)
                              .resetToken();
                          if (!context.mounted) return;
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(
                              content: Text(
                                err == null
                                    ? 'Calendar token reset — old subscriptions stop working'
                                    : 'Failed: $err',
                              ),
                            ),
                          );
                        },
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          Text(
            'Subscribe in Apple Calendar, Google Calendar, or Outlook. Updates within 1 hour of publish.',
            style: BlockType.bodySm,
          ),
        ],
      ),
    );
  }
}

class _SettingRow extends StatelessWidget {
  const _SettingRow({required this.label, required this.value});
  final String label;
  final String value;
  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: BlockCard(
        child: Row(
          children: [
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    label.toUpperCase(),
                    style: BlockType.monoLabel.copyWith(fontSize: 10),
                  ),
                  const SizedBox(height: 2),
                  Text(value, style: BlockType.body),
                ],
              ),
            ),
            const Icon(Icons.chevron_right, color: BlockColors.ink3, size: 20),
          ],
        ),
      ),
    );
  }
}
