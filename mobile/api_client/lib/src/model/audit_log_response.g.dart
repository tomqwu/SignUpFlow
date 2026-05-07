// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'audit_log_response.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$AuditLogResponse extends AuditLogResponse {
  @override
  final String action;
  @override
  final BuiltMap<String, JsonObject?>? details;
  @override
  final String? errorMessage;
  @override
  final String id;
  @override
  final String? ipAddress;
  @override
  final String? organizationId;
  @override
  final String? resourceId;
  @override
  final String? resourceType;
  @override
  final String status;
  @override
  final DateTime timestamp;
  @override
  final String? userAgent;
  @override
  final String? userEmail;
  @override
  final String? userId;

  factory _$AuditLogResponse(
          [void Function(AuditLogResponseBuilder)? updates]) =>
      (AuditLogResponseBuilder()..update(updates))._build();

  _$AuditLogResponse._(
      {required this.action,
      this.details,
      this.errorMessage,
      required this.id,
      this.ipAddress,
      this.organizationId,
      this.resourceId,
      this.resourceType,
      required this.status,
      required this.timestamp,
      this.userAgent,
      this.userEmail,
      this.userId})
      : super._();
  @override
  AuditLogResponse rebuild(void Function(AuditLogResponseBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  AuditLogResponseBuilder toBuilder() =>
      AuditLogResponseBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is AuditLogResponse &&
        action == other.action &&
        details == other.details &&
        errorMessage == other.errorMessage &&
        id == other.id &&
        ipAddress == other.ipAddress &&
        organizationId == other.organizationId &&
        resourceId == other.resourceId &&
        resourceType == other.resourceType &&
        status == other.status &&
        timestamp == other.timestamp &&
        userAgent == other.userAgent &&
        userEmail == other.userEmail &&
        userId == other.userId;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, action.hashCode);
    _$hash = $jc(_$hash, details.hashCode);
    _$hash = $jc(_$hash, errorMessage.hashCode);
    _$hash = $jc(_$hash, id.hashCode);
    _$hash = $jc(_$hash, ipAddress.hashCode);
    _$hash = $jc(_$hash, organizationId.hashCode);
    _$hash = $jc(_$hash, resourceId.hashCode);
    _$hash = $jc(_$hash, resourceType.hashCode);
    _$hash = $jc(_$hash, status.hashCode);
    _$hash = $jc(_$hash, timestamp.hashCode);
    _$hash = $jc(_$hash, userAgent.hashCode);
    _$hash = $jc(_$hash, userEmail.hashCode);
    _$hash = $jc(_$hash, userId.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'AuditLogResponse')
          ..add('action', action)
          ..add('details', details)
          ..add('errorMessage', errorMessage)
          ..add('id', id)
          ..add('ipAddress', ipAddress)
          ..add('organizationId', organizationId)
          ..add('resourceId', resourceId)
          ..add('resourceType', resourceType)
          ..add('status', status)
          ..add('timestamp', timestamp)
          ..add('userAgent', userAgent)
          ..add('userEmail', userEmail)
          ..add('userId', userId))
        .toString();
  }
}

class AuditLogResponseBuilder
    implements Builder<AuditLogResponse, AuditLogResponseBuilder> {
  _$AuditLogResponse? _$v;

  String? _action;
  String? get action => _$this._action;
  set action(String? action) => _$this._action = action;

  MapBuilder<String, JsonObject?>? _details;
  MapBuilder<String, JsonObject?> get details =>
      _$this._details ??= MapBuilder<String, JsonObject?>();
  set details(MapBuilder<String, JsonObject?>? details) =>
      _$this._details = details;

  String? _errorMessage;
  String? get errorMessage => _$this._errorMessage;
  set errorMessage(String? errorMessage) => _$this._errorMessage = errorMessage;

  String? _id;
  String? get id => _$this._id;
  set id(String? id) => _$this._id = id;

  String? _ipAddress;
  String? get ipAddress => _$this._ipAddress;
  set ipAddress(String? ipAddress) => _$this._ipAddress = ipAddress;

  String? _organizationId;
  String? get organizationId => _$this._organizationId;
  set organizationId(String? organizationId) =>
      _$this._organizationId = organizationId;

  String? _resourceId;
  String? get resourceId => _$this._resourceId;
  set resourceId(String? resourceId) => _$this._resourceId = resourceId;

  String? _resourceType;
  String? get resourceType => _$this._resourceType;
  set resourceType(String? resourceType) => _$this._resourceType = resourceType;

  String? _status;
  String? get status => _$this._status;
  set status(String? status) => _$this._status = status;

  DateTime? _timestamp;
  DateTime? get timestamp => _$this._timestamp;
  set timestamp(DateTime? timestamp) => _$this._timestamp = timestamp;

  String? _userAgent;
  String? get userAgent => _$this._userAgent;
  set userAgent(String? userAgent) => _$this._userAgent = userAgent;

  String? _userEmail;
  String? get userEmail => _$this._userEmail;
  set userEmail(String? userEmail) => _$this._userEmail = userEmail;

  String? _userId;
  String? get userId => _$this._userId;
  set userId(String? userId) => _$this._userId = userId;

  AuditLogResponseBuilder() {
    AuditLogResponse._defaults(this);
  }

  AuditLogResponseBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _action = $v.action;
      _details = $v.details?.toBuilder();
      _errorMessage = $v.errorMessage;
      _id = $v.id;
      _ipAddress = $v.ipAddress;
      _organizationId = $v.organizationId;
      _resourceId = $v.resourceId;
      _resourceType = $v.resourceType;
      _status = $v.status;
      _timestamp = $v.timestamp;
      _userAgent = $v.userAgent;
      _userEmail = $v.userEmail;
      _userId = $v.userId;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(AuditLogResponse other) {
    _$v = other as _$AuditLogResponse;
  }

  @override
  void update(void Function(AuditLogResponseBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  AuditLogResponse build() => _build();

  _$AuditLogResponse _build() {
    _$AuditLogResponse _$result;
    try {
      _$result = _$v ??
          _$AuditLogResponse._(
            action: BuiltValueNullFieldError.checkNotNull(
                action, r'AuditLogResponse', 'action'),
            details: _details?.build(),
            errorMessage: errorMessage,
            id: BuiltValueNullFieldError.checkNotNull(
                id, r'AuditLogResponse', 'id'),
            ipAddress: ipAddress,
            organizationId: organizationId,
            resourceId: resourceId,
            resourceType: resourceType,
            status: BuiltValueNullFieldError.checkNotNull(
                status, r'AuditLogResponse', 'status'),
            timestamp: BuiltValueNullFieldError.checkNotNull(
                timestamp, r'AuditLogResponse', 'timestamp'),
            userAgent: userAgent,
            userEmail: userEmail,
            userId: userId,
          );
    } catch (_) {
      late String _$failedField;
      try {
        _$failedField = 'details';
        _details?.build();
      } catch (e) {
        throw BuiltValueNestedFieldError(
            r'AuditLogResponse', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
