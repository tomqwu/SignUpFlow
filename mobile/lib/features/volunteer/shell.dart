// Volunteer 3-tab shell: Schedule / Avail / Profile.
// Inbox is reachable only via deep-link or future notification dispatch —
// it's not in the tab bar (deferred from MVP per spec 022).

import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import 'package:signupflow_mobile/theme/colors.dart';

class VolunteerShell extends StatelessWidget {
  const VolunteerShell({required this.child, super.key});
  final Widget child;

  static const _routes = ['/v/schedule', '/v/availability', '/v/profile'];

  int _indexOf(String location) {
    for (var i = 0; i < _routes.length; i++) {
      if (location.startsWith(_routes[i])) return i;
    }
    return 0;
  }

  @override
  Widget build(BuildContext context) {
    final location = GoRouterState.of(context).uri.toString();
    final idx = _indexOf(location);
    return Scaffold(
      backgroundColor: BlockColors.bgApp,
      body: child,
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: idx,
        onTap: (i) => context.go(_routes[i]),
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.calendar_today_outlined), label: 'SCHEDULE'),
          BottomNavigationBarItem(icon: Icon(Icons.event_available_outlined), label: 'AVAIL'),
          BottomNavigationBarItem(icon: Icon(Icons.person_outline), label: 'PROFILE'),
        ],
      ),
    );
  }
}
