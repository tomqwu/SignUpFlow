// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'send_event_reminder_request.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$SendEventReminderRequest extends SendEventReminderRequest {
  @override
  final String eventId;
  @override
  final int? hoursBefore;
  @override
  final String? language;

  factory _$SendEventReminderRequest(
          [void Function(SendEventReminderRequestBuilder)? updates]) =>
      (SendEventReminderRequestBuilder()..update(updates))._build();

  _$SendEventReminderRequest._(
      {required this.eventId, this.hoursBefore, this.language})
      : super._();
  @override
  SendEventReminderRequest rebuild(
          void Function(SendEventReminderRequestBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  SendEventReminderRequestBuilder toBuilder() =>
      SendEventReminderRequestBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is SendEventReminderRequest &&
        eventId == other.eventId &&
        hoursBefore == other.hoursBefore &&
        language == other.language;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, eventId.hashCode);
    _$hash = $jc(_$hash, hoursBefore.hashCode);
    _$hash = $jc(_$hash, language.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'SendEventReminderRequest')
          ..add('eventId', eventId)
          ..add('hoursBefore', hoursBefore)
          ..add('language', language))
        .toString();
  }
}

class SendEventReminderRequestBuilder
    implements
        Builder<SendEventReminderRequest, SendEventReminderRequestBuilder> {
  _$SendEventReminderRequest? _$v;

  String? _eventId;
  String? get eventId => _$this._eventId;
  set eventId(String? eventId) => _$this._eventId = eventId;

  int? _hoursBefore;
  int? get hoursBefore => _$this._hoursBefore;
  set hoursBefore(int? hoursBefore) => _$this._hoursBefore = hoursBefore;

  String? _language;
  String? get language => _$this._language;
  set language(String? language) => _$this._language = language;

  SendEventReminderRequestBuilder() {
    SendEventReminderRequest._defaults(this);
  }

  SendEventReminderRequestBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _eventId = $v.eventId;
      _hoursBefore = $v.hoursBefore;
      _language = $v.language;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(SendEventReminderRequest other) {
    _$v = other as _$SendEventReminderRequest;
  }

  @override
  void update(void Function(SendEventReminderRequestBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  SendEventReminderRequest build() => _build();

  _$SendEventReminderRequest _build() {
    final _$result = _$v ??
        _$SendEventReminderRequest._(
          eventId: BuiltValueNullFieldError.checkNotNull(
              eventId, r'SendEventReminderRequest', 'eventId'),
          hoursBefore: hoursBefore,
          language: language,
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
