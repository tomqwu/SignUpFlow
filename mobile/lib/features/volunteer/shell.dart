// Volunteer 4-tab shell: Schedule / Avail / Inbox / Profile.
// Inbox got re-added in Sprint 8.10 once /notifications was registered.

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import 'package:signupflow_mobile/features/volunteer/inbox_provider.dart';
import 'package:signupflow_mobile/theme/colors.dart';

class VolunteerShell extends ConsumerWidget {
  const VolunteerShell({required this.child, super.key});
  final Widget child;

  static const _routes = [
    '/v/schedule',
    '/v/availability',
    '/v/inbox',
    '/v/profile',
  ];

  int _indexOf(String location) {
    for (var i = 0; i < _routes.length; i++) {
      if (location.startsWith(_routes[i])) return i;
    }
    return 0;
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final location = GoRouterState.of(context).uri.toString();
    final idx = _indexOf(location);
    final unread = ref.watch(inboxProvider).whenOrNull(data: (d) => d.unread) ?? 0;
    return Scaffold(
      backgroundColor: BlockColors.bgApp,
      body: child,
      bottomNavigationBar: BottomNavigationBar(
        type: BottomNavigationBarType.fixed,
        currentIndex: idx,
        onTap: (i) => context.go(_routes[i]),
        items: [
          const BottomNavigationBarItem(
            icon: Icon(Icons.calendar_today_outlined),
            label: 'SCHEDULE',
          ),
          const BottomNavigationBarItem(
            icon: Icon(Icons.event_available_outlined),
            label: 'AVAIL',
          ),
          BottomNavigationBarItem(
            icon: _InboxIcon(unread: unread),
            label: 'INBOX',
          ),
          const BottomNavigationBarItem(
            icon: Icon(Icons.person_outline),
            label: 'PROFILE',
          ),
        ],
      ),
    );
  }
}

class _InboxIcon extends StatelessWidget {
  const _InboxIcon({required this.unread});
  final int unread;

  @override
  Widget build(BuildContext context) {
    if (unread == 0) {
      return const Icon(Icons.inbox_outlined);
    }
    return Stack(
      clipBehavior: Clip.none,
      children: [
        const Icon(Icons.inbox_outlined),
        Positioned(
          right: -4,
          top: -2,
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 1),
            decoration: BoxDecoration(
              color: BlockColors.accent,
              borderRadius: BorderRadius.circular(8),
            ),
            constraints: const BoxConstraints(minWidth: 14, minHeight: 14),
            child: Text(
              unread > 9 ? '9+' : '$unread',
              style: const TextStyle(
                color: Colors.white,
                fontSize: 9,
                fontWeight: FontWeight.w700,
              ),
              textAlign: TextAlign.center,
            ),
          ),
        ),
      ],
    );
  }
}
