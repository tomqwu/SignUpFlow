//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

import 'dart:async';

import 'package:built_value/json_object.dart';
import 'package:built_value/serializer.dart';
import 'package:dio/dio.dart';

import 'package:signupflow_api/src/api_util.dart';
import 'package:signupflow_api/src/model/http_validation_error.dart';
import 'package:signupflow_api/src/model/list_response_audit_log_response.dart';

class AuditApi {

  final Dio _dio;

  final Serializers _serializers;

  const AuditApi(this._dio, this._serializers);

  /// List Audit Logs
  /// Return audit log rows scoped to the caller&#39;s organization.  Admin-only. Each call is itself recorded as a &#x60;data.exported&#x60; audit event so reads of the audit log are themselves auditable.
  ///
  /// Parameters:
  /// * [userId] - Filter by user_id
  /// * [action] - Filter by action (e.g., auth.login.success)
  /// * [resourceType] - Filter by resource_type
  /// * [startDate] - Inclusive lower bound on timestamp
  /// * [endDate] - Inclusive upper bound on timestamp
  /// * [status] - success / failure / denied
  /// * [limit] - Page size, max 200
  /// * [offset] - Number of rows to skip
  /// * [cancelToken] - A [CancelToken] that can be used to cancel the operation
  /// * [headers] - Can be used to add additional headers to the request
  /// * [extras] - Can be used to add flags to the request
  /// * [validateStatus] - A [ValidateStatus] callback that can be used to determine request success based on the HTTP status of the response
  /// * [onSendProgress] - A [ProgressCallback] that can be used to get the send progress
  /// * [onReceiveProgress] - A [ProgressCallback] that can be used to get the receive progress
  ///
  /// Returns a [Future] containing a [Response] with a [ListResponseAuditLogResponse] as data
  /// Throws [DioException] if API call or serialization fails
  Future<Response<ListResponseAuditLogResponse>> listAuditLogs({ 
    String? userId,
    String? action,
    String? resourceType,
    DateTime? startDate,
    DateTime? endDate,
    String? status,
    int? limit = 50,
    int? offset = 0,
    CancelToken? cancelToken,
    Map<String, dynamic>? headers,
    Map<String, dynamic>? extra,
    ValidateStatus? validateStatus,
    ProgressCallback? onSendProgress,
    ProgressCallback? onReceiveProgress,
  }) async {
    final _path = r'/api/v1/audit-logs';
    final _options = Options(
      method: r'GET',
      headers: <String, dynamic>{
        ...?headers,
      },
      extra: <String, dynamic>{
        'secure': <Map<String, String>>[
          {
            'type': 'http',
            'scheme': 'bearer',
            'name': 'HTTPBearer',
          },
        ],
        ...?extra,
      },
      validateStatus: validateStatus,
    );

    final _queryParameters = <String, dynamic>{
      r'user_id': encodeQueryParameter(_serializers, userId, const FullType(String)),
      r'action': encodeQueryParameter(_serializers, action, const FullType(String)),
      r'resource_type': encodeQueryParameter(_serializers, resourceType, const FullType(String)),
      r'start_date': encodeQueryParameter(_serializers, startDate, const FullType(DateTime)),
      r'end_date': encodeQueryParameter(_serializers, endDate, const FullType(DateTime)),
      r'status': encodeQueryParameter(_serializers, status, const FullType(String)),
      if (limit != null) r'limit': encodeQueryParameter(_serializers, limit, const FullType(int)),
      if (offset != null) r'offset': encodeQueryParameter(_serializers, offset, const FullType(int)),
    };

    final _response = await _dio.request<Object>(
      _path,
      options: _options,
      queryParameters: _queryParameters,
      cancelToken: cancelToken,
      onSendProgress: onSendProgress,
      onReceiveProgress: onReceiveProgress,
    );

    ListResponseAuditLogResponse? _responseData;

    try {
      final rawResponse = _response.data;
      _responseData = rawResponse == null ? null : _serializers.deserialize(
        rawResponse,
        specifiedType: const FullType(ListResponseAuditLogResponse),
      ) as ListResponseAuditLogResponse;

    } catch (error, stackTrace) {
      throw DioException(
        requestOptions: _response.requestOptions,
        response: _response,
        type: DioExceptionType.unknown,
        error: error,
        stackTrace: stackTrace,
      );
    }

    return Response<ListResponseAuditLogResponse>(
      data: _responseData,
      headers: _response.headers,
      isRedirect: _response.isRedirect,
      requestOptions: _response.requestOptions,
      redirects: _response.redirects,
      statusCode: _response.statusCode,
      statusMessage: _response.statusMessage,
      extra: _response.extra,
    );
  }

}
