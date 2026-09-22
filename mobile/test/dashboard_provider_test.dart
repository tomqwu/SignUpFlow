// dashboardProvider decoding test — serves the real backend response shapes
// of GET /api/v1/analytics/{org_id}/volunteer-stats and /schedule-health
// (see api/routers/analytics.py) through a stub dio and asserts the KPI
// values the dashboard tiles render.

import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:signupflow_api/signupflow_api.dart' as api;
import 'package:signupflow_mobile/api/api_client.dart';
import 'package:signupflow_mobile/auth/auth_provider.dart';
import 'package:signupflow_mobile/features/admin/dashboard_provider.dart';

class _SignedInAdmin extends AuthController {
  @override
  AuthState build() => const AuthState(
        role: AuthRole.admin,
        token: 'test-token',
        orgId: 'hcc',
      );
}

Future<DashboardData> _loadDashboard(Map<String, dynamic> scheduleHealth) async {
  final dio = Dio();
  dio.interceptors.add(
    InterceptorsWrapper(
      onRequest: (options, handler) {
        final Object data;
        if (options.path.endsWith('/volunteer-stats')) {
          data = {
            'org_id': 'hcc',
            'period_days': 30,
            'total_volunteers': 60,
            'active_volunteers': 47,
            'total_assignments': 120,
            'participation_rate': 78.3,
            'top_volunteers': <Object>[],
          };
        } else if (options.path.endsWith('/schedule-health')) {
          data = scheduleHealth;
        } else {
          data = {'items': <Object>[], 'total': 0, 'limit': 10, 'offset': 0};
        }
        handler.resolve(
          Response<Object>(requestOptions: options, statusCode: 200, data: data),
        );
      },
    ),
  );
  final container = ProviderContainer(
    overrides: [
      authProvider.overrideWith(_SignedInAdmin.new),
      signupflowApiProvider.overrideWithValue(api.SignupflowApi(dio: dio)),
    ],
  );
  addTearDown(container.dispose);
  addTearDown(dio.close);
  return container.read(dashboardProvider.future);
}

void main() {
  test('reads upcoming events and latest solution health score', () async {
    final data = await _loadDashboard({
      'org_id': 'hcc',
      'upcoming_events': 12,
      'events_with_assignments': 9,
      'coverage_rate': 75.0,
      'latest_solution': {
        'id': 142,
        'health_score': 98.4,
        'assignment_count': 24,
        'created_at': '2026-05-07T14:14:00',
      },
    });

    expect(data.activeVolunteers, 47);
    expect(data.upcomingEvents, 12);
    expect(data.healthScore, 98.4);
  });

  test('health score is null when no solution exists yet', () async {
    final data = await _loadDashboard({
      'org_id': 'hcc',
      'upcoming_events': 3,
      'events_with_assignments': 0,
      'coverage_rate': 0.0,
      'latest_solution': null,
    });

    expect(data.upcomingEvents, 3);
    expect(data.healthScore, isNull);
  });
}
