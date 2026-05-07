// GoRouter — declarative routing with role-aware redirects.
// Routes:
//   /login                       — pre-auth (default)
//   /invitation                  — deep-link invitation accept (PR 7.2)
//   /v/{schedule,availability,profile,inbox} — volunteer tabs
//   /v/assignment/:id            — pushed assignment detail
//   /a/{dashboard,people,events,solver} — admin tabs
//   /a/solution/:id              — pushed solution review
//   /a/{compare,publish}         — pushed admin actions

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import 'package:signupflow_mobile/auth/auth_provider.dart';
import 'package:signupflow_mobile/features/admin/compare_screen.dart';
import 'package:signupflow_mobile/features/admin/dashboard_screen.dart';
import 'package:signupflow_mobile/features/admin/events_screen.dart';
import 'package:signupflow_mobile/features/admin/people_screen.dart';
import 'package:signupflow_mobile/features/admin/publish_screen.dart';
import 'package:signupflow_mobile/features/admin/shell.dart';
import 'package:signupflow_mobile/features/admin/solution_review_screen.dart';
import 'package:signupflow_mobile/features/admin/solver_screen.dart';
import 'package:signupflow_mobile/features/auth/invitation_screen.dart';
import 'package:signupflow_mobile/features/auth/login_screen.dart';
import 'package:signupflow_mobile/features/volunteer/assignment_detail_screen.dart';
import 'package:signupflow_mobile/features/volunteer/availability_screen.dart';
import 'package:signupflow_mobile/features/volunteer/inbox_screen.dart';
import 'package:signupflow_mobile/features/volunteer/profile_screen.dart';
import 'package:signupflow_mobile/features/volunteer/schedule_screen.dart';
import 'package:signupflow_mobile/features/volunteer/shell.dart';

GoRouter buildRouter(WidgetRef ref) {
  return GoRouter(
    initialLocation: '/login',
    redirect: (context, state) {
      final auth = ref.read(authProvider);
      final loc = state.matchedLocation;
      final isAuth = loc == '/login' || loc == '/invitation';

      if (auth.role == AuthRole.unauth && !isAuth) return '/login';
      if (auth.role == AuthRole.volunteer && loc.startsWith('/a/')) {
        return '/v/schedule';
      }
      // Admin can read /v/* freely (intentional, e.g. to preview the volunteer
      // experience from inside an admin role).
      return null;
    },
    routes: [
      GoRoute(path: '/login', builder: (_, __) => const LoginScreen()),
      GoRoute(path: '/invitation', builder: (_, __) => const InvitationScreen()),

      ShellRoute(
        builder: (_, __, child) => VolunteerShell(child: child),
        routes: [
          GoRoute(
            path: '/v/schedule',
            builder: (_, __) => const VolunteerScheduleScreen(),
          ),
          GoRoute(
            path: '/v/availability',
            builder: (_, __) => const AvailabilityScreen(),
          ),
          GoRoute(
            path: '/v/inbox',
            builder: (_, __) => const InboxScreen(),
          ),
          GoRoute(
            path: '/v/profile',
            builder: (_, __) => const VolunteerProfileScreen(),
          ),
        ],
      ),
      GoRoute(
        path: '/v/assignment/:id',
        builder: (_, state) =>
            AssignmentDetailScreen(assignmentId: state.pathParameters['id']!),
      ),

      ShellRoute(
        builder: (_, __, child) => AdminShell(child: child),
        routes: [
          GoRoute(
            path: '/a/dashboard',
            builder: (_, __) => const DashboardScreen(),
          ),
          GoRoute(
            path: '/a/people',
            builder: (_, __) => const PeopleScreen(),
          ),
          GoRoute(
            path: '/a/events',
            builder: (_, __) => const EventsScreen(),
          ),
          GoRoute(
            path: '/a/solver',
            builder: (_, __) => const SolverScreen(),
          ),
        ],
      ),
      GoRoute(
        path: '/a/solution/:id',
        builder: (_, state) =>
            SolutionReviewScreen(solutionId: state.pathParameters['id']!),
      ),
      GoRoute(path: '/a/compare', builder: (_, __) => const CompareScreen()),
      GoRoute(path: '/a/publish', builder: (_, __) => const PublishScreen()),
    ],
    errorBuilder: (_, state) => Scaffold(
      body: Center(
        child: Text('No route for ${state.uri}', textAlign: TextAlign.center),
      ),
    ),
  );
}
