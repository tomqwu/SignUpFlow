// Compare diff provider — Sprint 7.10.

import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:signupflow_api/signupflow_api.dart' as api;
import 'package:signupflow_mobile/api/api_client.dart';

@immutable
class CompareIds {
  const CompareIds({required this.a, required this.b});
  final int a;
  final int b;

  @override
  bool operator ==(Object other) =>
      other is CompareIds && other.a == a && other.b == b;
  @override
  int get hashCode => Object.hash(a, b);
}

final compareDiffProvider =
    FutureProvider.family<api.SolutionDiffResponse, CompareIds>((ref, ids) async {
  final apiClient = ref.watch(signupflowApiProvider);
  final res = await apiClient.getSolutionsApi().compareSolutions(
        solutionAId: ids.a,
        solutionBId: ids.b,
      );
  final body = res.data;
  if (body == null) {
    throw StateError('Empty compare response for ${ids.a} vs ${ids.b}');
  }
  return body;
});
