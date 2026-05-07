// GET /people/me — returns the authenticated person + role array.

import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:signupflow_mobile/api/api_client.dart';
import 'package:signupflow_mobile/api/models.dart';

class PeopleApi {
  PeopleApi(this._dio);
  final Dio _dio;

  Future<PersonMe> me() async {
    final res = await _dio.get<Map<String, dynamic>>('/people/me');
    if (res.data == null) {
      throw const FormatException('empty /people/me response');
    }
    return PersonMe.fromJson(res.data!);
  }
}

final peopleApiProvider = Provider<PeopleApi>((ref) {
  return PeopleApi(ref.watch(dioProvider));
});
