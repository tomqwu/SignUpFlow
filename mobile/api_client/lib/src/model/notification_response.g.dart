// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'notification_response.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$NotificationResponse extends NotificationResponse {
  @override
  final DateTime? clickedAt;
  @override
  final DateTime createdAt;
  @override
  final DateTime? deliveredAt;
  @override
  final String? errorMessage;
  @override
  final String? eventId;
  @override
  final int id;
  @override
  final DateTime? openedAt;
  @override
  final String orgId;
  @override
  final String recipientId;
  @override
  final int retryCount;
  @override
  final String? sendgridMessageId;
  @override
  final DateTime? sentAt;
  @override
  final String status;
  @override
  final BuiltMap<String, JsonObject?>? templateData;
  @override
  final String type;

  factory _$NotificationResponse(
          [void Function(NotificationResponseBuilder)? updates]) =>
      (NotificationResponseBuilder()..update(updates))._build();

  _$NotificationResponse._(
      {this.clickedAt,
      required this.createdAt,
      this.deliveredAt,
      this.errorMessage,
      this.eventId,
      required this.id,
      this.openedAt,
      required this.orgId,
      required this.recipientId,
      required this.retryCount,
      this.sendgridMessageId,
      this.sentAt,
      required this.status,
      this.templateData,
      required this.type})
      : super._();
  @override
  NotificationResponse rebuild(
          void Function(NotificationResponseBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  NotificationResponseBuilder toBuilder() =>
      NotificationResponseBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is NotificationResponse &&
        clickedAt == other.clickedAt &&
        createdAt == other.createdAt &&
        deliveredAt == other.deliveredAt &&
        errorMessage == other.errorMessage &&
        eventId == other.eventId &&
        id == other.id &&
        openedAt == other.openedAt &&
        orgId == other.orgId &&
        recipientId == other.recipientId &&
        retryCount == other.retryCount &&
        sendgridMessageId == other.sendgridMessageId &&
        sentAt == other.sentAt &&
        status == other.status &&
        templateData == other.templateData &&
        type == other.type;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, clickedAt.hashCode);
    _$hash = $jc(_$hash, createdAt.hashCode);
    _$hash = $jc(_$hash, deliveredAt.hashCode);
    _$hash = $jc(_$hash, errorMessage.hashCode);
    _$hash = $jc(_$hash, eventId.hashCode);
    _$hash = $jc(_$hash, id.hashCode);
    _$hash = $jc(_$hash, openedAt.hashCode);
    _$hash = $jc(_$hash, orgId.hashCode);
    _$hash = $jc(_$hash, recipientId.hashCode);
    _$hash = $jc(_$hash, retryCount.hashCode);
    _$hash = $jc(_$hash, sendgridMessageId.hashCode);
    _$hash = $jc(_$hash, sentAt.hashCode);
    _$hash = $jc(_$hash, status.hashCode);
    _$hash = $jc(_$hash, templateData.hashCode);
    _$hash = $jc(_$hash, type.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'NotificationResponse')
          ..add('clickedAt', clickedAt)
          ..add('createdAt', createdAt)
          ..add('deliveredAt', deliveredAt)
          ..add('errorMessage', errorMessage)
          ..add('eventId', eventId)
          ..add('id', id)
          ..add('openedAt', openedAt)
          ..add('orgId', orgId)
          ..add('recipientId', recipientId)
          ..add('retryCount', retryCount)
          ..add('sendgridMessageId', sendgridMessageId)
          ..add('sentAt', sentAt)
          ..add('status', status)
          ..add('templateData', templateData)
          ..add('type', type))
        .toString();
  }
}

class NotificationResponseBuilder
    implements Builder<NotificationResponse, NotificationResponseBuilder> {
  _$NotificationResponse? _$v;

  DateTime? _clickedAt;
  DateTime? get clickedAt => _$this._clickedAt;
  set clickedAt(DateTime? clickedAt) => _$this._clickedAt = clickedAt;

  DateTime? _createdAt;
  DateTime? get createdAt => _$this._createdAt;
  set createdAt(DateTime? createdAt) => _$this._createdAt = createdAt;

  DateTime? _deliveredAt;
  DateTime? get deliveredAt => _$this._deliveredAt;
  set deliveredAt(DateTime? deliveredAt) => _$this._deliveredAt = deliveredAt;

  String? _errorMessage;
  String? get errorMessage => _$this._errorMessage;
  set errorMessage(String? errorMessage) => _$this._errorMessage = errorMessage;

  String? _eventId;
  String? get eventId => _$this._eventId;
  set eventId(String? eventId) => _$this._eventId = eventId;

  int? _id;
  int? get id => _$this._id;
  set id(int? id) => _$this._id = id;

  DateTime? _openedAt;
  DateTime? get openedAt => _$this._openedAt;
  set openedAt(DateTime? openedAt) => _$this._openedAt = openedAt;

  String? _orgId;
  String? get orgId => _$this._orgId;
  set orgId(String? orgId) => _$this._orgId = orgId;

  String? _recipientId;
  String? get recipientId => _$this._recipientId;
  set recipientId(String? recipientId) => _$this._recipientId = recipientId;

  int? _retryCount;
  int? get retryCount => _$this._retryCount;
  set retryCount(int? retryCount) => _$this._retryCount = retryCount;

  String? _sendgridMessageId;
  String? get sendgridMessageId => _$this._sendgridMessageId;
  set sendgridMessageId(String? sendgridMessageId) =>
      _$this._sendgridMessageId = sendgridMessageId;

  DateTime? _sentAt;
  DateTime? get sentAt => _$this._sentAt;
  set sentAt(DateTime? sentAt) => _$this._sentAt = sentAt;

  String? _status;
  String? get status => _$this._status;
  set status(String? status) => _$this._status = status;

  MapBuilder<String, JsonObject?>? _templateData;
  MapBuilder<String, JsonObject?> get templateData =>
      _$this._templateData ??= MapBuilder<String, JsonObject?>();
  set templateData(MapBuilder<String, JsonObject?>? templateData) =>
      _$this._templateData = templateData;

  String? _type;
  String? get type => _$this._type;
  set type(String? type) => _$this._type = type;

  NotificationResponseBuilder() {
    NotificationResponse._defaults(this);
  }

  NotificationResponseBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _clickedAt = $v.clickedAt;
      _createdAt = $v.createdAt;
      _deliveredAt = $v.deliveredAt;
      _errorMessage = $v.errorMessage;
      _eventId = $v.eventId;
      _id = $v.id;
      _openedAt = $v.openedAt;
      _orgId = $v.orgId;
      _recipientId = $v.recipientId;
      _retryCount = $v.retryCount;
      _sendgridMessageId = $v.sendgridMessageId;
      _sentAt = $v.sentAt;
      _status = $v.status;
      _templateData = $v.templateData?.toBuilder();
      _type = $v.type;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(NotificationResponse other) {
    _$v = other as _$NotificationResponse;
  }

  @override
  void update(void Function(NotificationResponseBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  NotificationResponse build() => _build();

  _$NotificationResponse _build() {
    _$NotificationResponse _$result;
    try {
      _$result = _$v ??
          _$NotificationResponse._(
            clickedAt: clickedAt,
            createdAt: BuiltValueNullFieldError.checkNotNull(
                createdAt, r'NotificationResponse', 'createdAt'),
            deliveredAt: deliveredAt,
            errorMessage: errorMessage,
            eventId: eventId,
            id: BuiltValueNullFieldError.checkNotNull(
                id, r'NotificationResponse', 'id'),
            openedAt: openedAt,
            orgId: BuiltValueNullFieldError.checkNotNull(
                orgId, r'NotificationResponse', 'orgId'),
            recipientId: BuiltValueNullFieldError.checkNotNull(
                recipientId, r'NotificationResponse', 'recipientId'),
            retryCount: BuiltValueNullFieldError.checkNotNull(
                retryCount, r'NotificationResponse', 'retryCount'),
            sendgridMessageId: sendgridMessageId,
            sentAt: sentAt,
            status: BuiltValueNullFieldError.checkNotNull(
                status, r'NotificationResponse', 'status'),
            templateData: _templateData?.build(),
            type: BuiltValueNullFieldError.checkNotNull(
                type, r'NotificationResponse', 'type'),
          );
    } catch (_) {
      late String _$failedField;
      try {
        _$failedField = 'templateData';
        _templateData?.build();
      } catch (e) {
        throw BuiltValueNestedFieldError(
            r'NotificationResponse', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
