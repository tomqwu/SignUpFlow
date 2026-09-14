// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'send_assignment_notification_request.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$SendAssignmentNotificationRequest
    extends SendAssignmentNotificationRequest {
  @override
  final int assignmentId;
  @override
  final String eventId;
  @override
  final String? language;
  @override
  final String personId;

  factory _$SendAssignmentNotificationRequest(
          [void Function(SendAssignmentNotificationRequestBuilder)? updates]) =>
      (SendAssignmentNotificationRequestBuilder()..update(updates))._build();

  _$SendAssignmentNotificationRequest._(
      {required this.assignmentId,
      required this.eventId,
      this.language,
      required this.personId})
      : super._();
  @override
  SendAssignmentNotificationRequest rebuild(
          void Function(SendAssignmentNotificationRequestBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  SendAssignmentNotificationRequestBuilder toBuilder() =>
      SendAssignmentNotificationRequestBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is SendAssignmentNotificationRequest &&
        assignmentId == other.assignmentId &&
        eventId == other.eventId &&
        language == other.language &&
        personId == other.personId;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, assignmentId.hashCode);
    _$hash = $jc(_$hash, eventId.hashCode);
    _$hash = $jc(_$hash, language.hashCode);
    _$hash = $jc(_$hash, personId.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'SendAssignmentNotificationRequest')
          ..add('assignmentId', assignmentId)
          ..add('eventId', eventId)
          ..add('language', language)
          ..add('personId', personId))
        .toString();
  }
}

class SendAssignmentNotificationRequestBuilder
    implements
        Builder<SendAssignmentNotificationRequest,
            SendAssignmentNotificationRequestBuilder> {
  _$SendAssignmentNotificationRequest? _$v;

  int? _assignmentId;
  int? get assignmentId => _$this._assignmentId;
  set assignmentId(int? assignmentId) => _$this._assignmentId = assignmentId;

  String? _eventId;
  String? get eventId => _$this._eventId;
  set eventId(String? eventId) => _$this._eventId = eventId;

  String? _language;
  String? get language => _$this._language;
  set language(String? language) => _$this._language = language;

  String? _personId;
  String? get personId => _$this._personId;
  set personId(String? personId) => _$this._personId = personId;

  SendAssignmentNotificationRequestBuilder() {
    SendAssignmentNotificationRequest._defaults(this);
  }

  SendAssignmentNotificationRequestBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _assignmentId = $v.assignmentId;
      _eventId = $v.eventId;
      _language = $v.language;
      _personId = $v.personId;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(SendAssignmentNotificationRequest other) {
    _$v = other as _$SendAssignmentNotificationRequest;
  }

  @override
  void update(
      void Function(SendAssignmentNotificationRequestBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  SendAssignmentNotificationRequest build() => _build();

  _$SendAssignmentNotificationRequest _build() {
    final _$result = _$v ??
        _$SendAssignmentNotificationRequest._(
          assignmentId: BuiltValueNullFieldError.checkNotNull(assignmentId,
              r'SendAssignmentNotificationRequest', 'assignmentId'),
          eventId: BuiltValueNullFieldError.checkNotNull(
              eventId, r'SendAssignmentNotificationRequest', 'eventId'),
          language: language,
          personId: BuiltValueNullFieldError.checkNotNull(
              personId, r'SendAssignmentNotificationRequest', 'personId'),
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
