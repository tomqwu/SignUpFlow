// Admin People — Sprint 7.8.
// Visual target: mobile/prototype/screenshots/v2/09-a-people.png.

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:signupflow_api/signupflow_api.dart' as api;
import 'package:signupflow_mobile/features/admin/people_provider.dart';
import 'package:signupflow_mobile/theme/colors.dart';
import 'package:signupflow_mobile/theme/components.dart';
import 'package:signupflow_mobile/theme/typography.dart';

class PeopleScreen extends ConsumerStatefulWidget {
  const PeopleScreen({super.key});

  @override
  ConsumerState<PeopleScreen> createState() => _PeopleScreenState();
}

class _PeopleScreenState extends ConsumerState<PeopleScreen> {
  String _query = '';

  @override
  Widget build(BuildContext context) {
    final asyncData = ref.watch(peopleProvider);
    return Scaffold(
      body: SafeArea(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 20),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.end,
                children: [
                  TextButton(
                    onPressed: () => _openInviteSheet(context),
                    style: TextButton.styleFrom(foregroundColor: BlockColors.accent),
                    child: Text(
                      'INVITE',
                      style: BlockType.monoLabel.copyWith(
                        color: BlockColors.accent,
                        fontSize: 13,
                      ),
                    ),
                  ),
                ],
              ),
            ),
            asyncData.when(
              loading: () => const SizedBox.shrink(),
              error: (_, __) => const SizedBox.shrink(),
              data: (people) => PageTitle(
                'People',
                trailingCount: '${people.length}',
              ),
            ),
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 0, 16, 12),
              child: _SearchField(onChanged: (v) => setState(() => _query = v.trim().toLowerCase())),
            ),
            Expanded(
              child: asyncData.when(
                loading: () => const Center(child: CircularProgressIndicator()),
                error: (e, _) => Center(
                  child: Padding(
                    padding: const EdgeInsets.all(24),
                    child: Text('Failed to load: $e', style: BlockType.bodySm),
                  ),
                ),
                data: (people) {
                  final filtered = _query.isEmpty
                      ? people
                      : people.where((p) {
                          final hay = '${p.name} ${p.email ?? ''}'.toLowerCase();
                          return hay.contains(_query);
                        }).toList();
                  if (filtered.isEmpty) {
                    return Center(
                      child: Padding(
                        padding: const EdgeInsets.all(24),
                        child: Text(
                          _query.isEmpty
                              ? 'No people yet. Tap INVITE to add one.'
                              : 'No matches for "$_query".',
                          style: BlockType.bodySm,
                          textAlign: TextAlign.center,
                        ),
                      ),
                    );
                  }
                  return ListView.builder(
                    padding: const EdgeInsets.fromLTRB(16, 0, 16, 96),
                    itemCount: filtered.length,
                    itemBuilder: (ctx, i) => _PersonRow(person: filtered[i]),
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _openInviteSheet(BuildContext context) async {
    final nameCtrl = TextEditingController();
    final emailCtrl = TextEditingController();
    final roles = {'volunteer'};

    final ok = await showModalBottomSheet<bool>(
      context: context,
      isScrollControlled: true,
      backgroundColor: BlockColors.bgCard,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (sheetCtx) => StatefulBuilder(
        builder: (innerCtx, setLocal) {
          return Padding(
            padding: EdgeInsets.fromLTRB(
              20,
              16,
              20,
              MediaQuery.of(innerCtx).viewInsets.bottom + 20,
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text('INVITE PERSON', style: BlockType.monoLabel.copyWith(color: BlockColors.ink1)),
                const SizedBox(height: 12),
                TextField(
                  controller: nameCtrl,
                  autofocus: true,
                  style: BlockType.body,
                  decoration: const InputDecoration(
                    labelText: 'Full name',
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 8),
                TextField(
                  controller: emailCtrl,
                  keyboardType: TextInputType.emailAddress,
                  style: BlockType.body,
                  decoration: const InputDecoration(
                    labelText: 'Email',
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 12),
                Wrap(
                  spacing: 8,
                  children: ['volunteer', 'admin']
                      .map(
                        (r) => FilterChip(
                          selected: roles.contains(r),
                          label: Text(r.toUpperCase()),
                          onSelected: (sel) => setLocal(() {
                            if (sel) {
                              roles.add(r);
                            } else {
                              roles.remove(r);
                            }
                          }),
                        ),
                      )
                      .toList(),
                ),
                const SizedBox(height: 14),
                Row(
                  children: [
                    Expanded(
                      child: BlockButton(
                        label: 'Cancel',
                        kind: BlockButtonKind.secondary,
                        onPressed: () => Navigator.of(sheetCtx).pop(false),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: BlockButton(
                        label: 'Send invite',
                        onPressed: () async {
                          if (nameCtrl.text.trim().isEmpty || emailCtrl.text.trim().isEmpty) {
                            ScaffoldMessenger.of(innerCtx).showSnackBar(
                              const SnackBar(content: Text('Name and email required')),
                            );
                            return;
                          }
                          if (roles.isEmpty) roles.add('volunteer');
                          final err = await ref
                              .read(inviteControllerProvider.notifier)
                              .invite(
                                name: nameCtrl.text.trim(),
                                email: emailCtrl.text.trim(),
                                roles: roles.toList(),
                              );
                          if (!innerCtx.mounted) return;
                          if (err != null) {
                            ScaffoldMessenger.of(innerCtx).showSnackBar(
                              SnackBar(content: Text('Failed: $err')),
                            );
                            return;
                          }
                          Navigator.of(sheetCtx).pop(true);
                        },
                      ),
                    ),
                  ],
                ),
              ],
            ),
          );
        },
      ),
    );

    if ((ok ?? false) && context.mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Invitation sent')),
      );
    }
  }
}

class _SearchField extends StatelessWidget {
  const _SearchField({required this.onChanged});
  final ValueChanged<String> onChanged;

  @override
  Widget build(BuildContext context) {
    return BlockCard(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
      child: Row(
        children: [
          const Icon(Icons.search, color: BlockColors.ink3, size: 18),
          const SizedBox(width: 8),
          Expanded(
            child: TextField(
              onChanged: onChanged,
              style: BlockType.body,
              decoration: InputDecoration(
                hintText: 'Search by name or email…',
                hintStyle: BlockType.body.copyWith(color: BlockColors.ink3),
                border: InputBorder.none,
                isDense: true,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _PersonRow extends StatelessWidget {
  const _PersonRow({required this.person});
  final api.PersonResponse person;

  @override
  Widget build(BuildContext context) {
    final email = person.email ?? '—';
    final roles = person.roles?.toList() ?? const <String>[];
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: BlockCard(
        padding: const EdgeInsets.all(12),
        child: Row(
          children: [
            AvatarBadge(name: person.name),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(person.name, style: BlockType.subhead),
                  const SizedBox(height: 2),
                  Text(email, style: BlockType.bodySm),
                  const SizedBox(height: 6),
                  Wrap(
                    spacing: 4,
                    children: [for (final r in roles) RoleChip(r)],
                  ),
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
