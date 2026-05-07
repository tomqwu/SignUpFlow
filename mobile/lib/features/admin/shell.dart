// Admin 4-tab shell: Home (Dashboard) / People / Events / Solver.
// Compare and Publish are reachable as pushed actions inside Solution Review.

import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import 'package:signupflow_mobile/theme/colors.dart';

class AdminShell extends StatelessWidget {
  const AdminShell({required this.child, super.key});
  final Widget child;

  static const _routes = [
    '/a/dashboard',
    '/a/people',
    '/a/events',
    '/a/solver',
  ];

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
          BottomNavigationBarItem(icon: Icon(Icons.home_outlined), label: 'HOME'),
          BottomNavigationBarItem(icon: Icon(Icons.people_outline), label: 'PEOPLE'),
          BottomNavigationBarItem(icon: Icon(Icons.grid_view_outlined), label: 'EVENTS'),
          BottomNavigationBarItem(icon: Icon(Icons.settings_outlined), label: 'SOLVER'),
        ],
      ),
    );
  }
}
