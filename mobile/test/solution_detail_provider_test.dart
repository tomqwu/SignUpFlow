import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:signupflow_api/signupflow_api.dart' as api;
import 'package:signupflow_mobile/api/api_client.dart';
import 'package:signupflow_mobile/features/admin/solver_provider.dart';

void main() {
  test('solution still loads when optional stats request fails', () async {
    final dio = Dio();
    dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) {
          if (options.path.endsWith('/stats')) {
            handler.reject(DioException(requestOptions: options));
          } else {
            handler.resolve(
              Response<Map<String, dynamic>>(
                requestOptions: options,
                statusCode: 200,
                data: {
                  'id': 142,
                  'org_id': 'sandbox',
                  'created_at': '2026-05-07T14:14:00Z',
                  'hard_violations': 0,
                  'health_score': 98,
                  'soft_score': 1.5,
                  'solve_ms': 274,
                },
              ),
            );
          }
        },
      ),
    );
    final container = ProviderContainer(
      overrides: [
        signupflowApiProvider.overrideWithValue(api.SignupflowApi(dio: dio)),
      ],
    );
    addTearDown(container.dispose);
    addTearDown(dio.close);
    final result = await container.read(solutionDetailProvider(142).future);
    expect(result.solution.id, 142);
    expect(result.stats, isNull);
  });
}
