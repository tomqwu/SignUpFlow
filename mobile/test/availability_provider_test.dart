// availabilityProvider decoding test — serves the real backend response
// shapes of GET /api/v1/availability/{person_id}/timeoff and /exceptions
// (see api/routers/availability.py) through a stub dio and asserts the
// time-off entries the availability calendar renders.

import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:signupflow_api/signupflow_api.dart' as api;
import 'package:signupflow_mobile/api/api_client.dart';
import 'package:signupflow_mobile/auth/auth_provider.dart';
import 'package:signupflow_mobile/features/volunteer/availability_provider.dart';

class _SignedInVolunteer extends AuthController {
  @override
  AuthState build() => const AuthState(
        role: AuthRole.volunteer,
        token: 'test-token',
        personId: 'p_alice',
        orgId: 'hcc',
      );
}

Future<AvailabilityData> _loadAvailability(Map<String, dynamic> timeoff) async {
  final dio = Dio();
  dio.interceptors.add(
    InterceptorsWrapper(
      onRequest: (options, handler) {
        final Object data;
        if (options.path.endsWith('/p_alice/timeoff')) {
          data = timeoff;
        } else if (options.path.endsWith('/p_alice/exceptions')) {
          data = [
            {'id': 3, 'exception_date': '2026-10-04'},
          ];
        } else {
          handler.reject(DioException(requestOptions: options));
          return;
        }
        handler.resolve(
          Response<Object>(requestOptions: options, statusCode: 200, data: data),
        );
      },
    ),
  );
  final container = ProviderContainer(
    overrides: [
      authProvider.overrideWith(_SignedInVolunteer.new),
      signupflowApiProvider.overrideWithValue(api.SignupflowApi(dio: dio)),
    ],
  );
  addTearDown(container.dispose);
  addTearDown(dio.close);
  return container.read(availabilityProvider.future);
}

void main() {
  test('decodes time-off periods sorted by start date', () async {
    final data = await _loadAvailability({
      'timeoff': [
        {
          'id': 8,
          'start_date': '2026-12-24',
          'end_date': '2026-12-26',
          'reason': null,
        },
        {
          'id': 7,
          'start_date': '2026-11-02',
          'end_date': '2026-11-03',
          'reason': 'Family trip',
        },
      ],
      'total': 2,
    });

    expect(data.entries.map((e) => e.id), [7, 8]);
    expect(data.entries.first.startDate, DateTime(2026, 11, 2));
    expect(data.entries.first.endDate, DateTime(2026, 11, 3));
    expect(data.entries.first.reason, 'Family trip');
    expect(data.entries.last.reason, isNull);
    expect(data.exceptions.single.date, DateTime(2026, 10, 4));
    expect(data.blockedDays, contains(DateTime(2026, 12, 25)));
  });

  test('empty time-off response yields no entries', () async {
    final data = await _loadAvailability({'timeoff': <Object>[], 'total': 0});

    expect(data.entries, isEmpty);
    expect(data.exceptions, hasLength(1));
  });
}
