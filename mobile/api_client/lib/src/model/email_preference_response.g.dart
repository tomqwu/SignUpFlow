// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'email_preference_response.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$EmailPreferenceResponse extends EmailPreferenceResponse {
  @override
  final int? digestHour;
  @override
  final BuiltList<String>? enabledTypes;
  @override
  final String? frequency;
  @override
  final int? id;
  @override
  final String? language;
  @override
  final String orgId;
  @override
  final String personId;
  @override
  final String? timezone;
  @override
  final String? unsubscribeToken;
  @override
  final DateTime? updatedAt;

  factory _$EmailPreferenceResponse(
          [void Function(EmailPreferenceResponseBuilder)? updates]) =>
      (EmailPreferenceResponseBuilder()..update(updates))._build();

  _$EmailPreferenceResponse._(
      {this.digestHour,
      this.enabledTypes,
      this.frequency,
      this.id,
      this.language,
      required this.orgId,
      required this.personId,
      this.timezone,
      this.unsubscribeToken,
      this.updatedAt})
      : super._();
  @override
  EmailPreferenceResponse rebuild(
          void Function(EmailPreferenceResponseBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  EmailPreferenceResponseBuilder toBuilder() =>
      EmailPreferenceResponseBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is EmailPreferenceResponse &&
        digestHour == other.digestHour &&
        enabledTypes == other.enabledTypes &&
        frequency == other.frequency &&
        id == other.id &&
        language == other.language &&
        orgId == other.orgId &&
        personId == other.personId &&
        timezone == other.timezone &&
        unsubscribeToken == other.unsubscribeToken &&
        updatedAt == other.updatedAt;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, digestHour.hashCode);
    _$hash = $jc(_$hash, enabledTypes.hashCode);
    _$hash = $jc(_$hash, frequency.hashCode);
    _$hash = $jc(_$hash, id.hashCode);
    _$hash = $jc(_$hash, language.hashCode);
    _$hash = $jc(_$hash, orgId.hashCode);
    _$hash = $jc(_$hash, personId.hashCode);
    _$hash = $jc(_$hash, timezone.hashCode);
    _$hash = $jc(_$hash, unsubscribeToken.hashCode);
    _$hash = $jc(_$hash, updatedAt.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'EmailPreferenceResponse')
          ..add('digestHour', digestHour)
          ..add('enabledTypes', enabledTypes)
          ..add('frequency', frequency)
          ..add('id', id)
          ..add('language', language)
          ..add('orgId', orgId)
          ..add('personId', personId)
          ..add('timezone', timezone)
          ..add('unsubscribeToken', unsubscribeToken)
          ..add('updatedAt', updatedAt))
        .toString();
  }
}

class EmailPreferenceResponseBuilder
    implements
        Builder<EmailPreferenceResponse, EmailPreferenceResponseBuilder> {
  _$EmailPreferenceResponse? _$v;

  int? _digestHour;
  int? get digestHour => _$this._digestHour;
  set digestHour(int? digestHour) => _$this._digestHour = digestHour;

  ListBuilder<String>? _enabledTypes;
  ListBuilder<String> get enabledTypes =>
      _$this._enabledTypes ??= ListBuilder<String>();
  set enabledTypes(ListBuilder<String>? enabledTypes) =>
      _$this._enabledTypes = enabledTypes;

  String? _frequency;
  String? get frequency => _$this._frequency;
  set frequency(String? frequency) => _$this._frequency = frequency;

  int? _id;
  int? get id => _$this._id;
  set id(int? id) => _$this._id = id;

  String? _language;
  String? get language => _$this._language;
  set language(String? language) => _$this._language = language;

  String? _orgId;
  String? get orgId => _$this._orgId;
  set orgId(String? orgId) => _$this._orgId = orgId;

  String? _personId;
  String? get personId => _$this._personId;
  set personId(String? personId) => _$this._personId = personId;

  String? _timezone;
  String? get timezone => _$this._timezone;
  set timezone(String? timezone) => _$this._timezone = timezone;

  String? _unsubscribeToken;
  String? get unsubscribeToken => _$this._unsubscribeToken;
  set unsubscribeToken(String? unsubscribeToken) =>
      _$this._unsubscribeToken = unsubscribeToken;

  DateTime? _updatedAt;
  DateTime? get updatedAt => _$this._updatedAt;
  set updatedAt(DateTime? updatedAt) => _$this._updatedAt = updatedAt;

  EmailPreferenceResponseBuilder() {
    EmailPreferenceResponse._defaults(this);
  }

  EmailPreferenceResponseBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _digestHour = $v.digestHour;
      _enabledTypes = $v.enabledTypes?.toBuilder();
      _frequency = $v.frequency;
      _id = $v.id;
      _language = $v.language;
      _orgId = $v.orgId;
      _personId = $v.personId;
      _timezone = $v.timezone;
      _unsubscribeToken = $v.unsubscribeToken;
      _updatedAt = $v.updatedAt;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(EmailPreferenceResponse other) {
    _$v = other as _$EmailPreferenceResponse;
  }

  @override
  void update(void Function(EmailPreferenceResponseBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  EmailPreferenceResponse build() => _build();

  _$EmailPreferenceResponse _build() {
    _$EmailPreferenceResponse _$result;
    try {
      _$result = _$v ??
          _$EmailPreferenceResponse._(
            digestHour: digestHour,
            enabledTypes: _enabledTypes?.build(),
            frequency: frequency,
            id: id,
            language: language,
            orgId: BuiltValueNullFieldError.checkNotNull(
                orgId, r'EmailPreferenceResponse', 'orgId'),
            personId: BuiltValueNullFieldError.checkNotNull(
                personId, r'EmailPreferenceResponse', 'personId'),
            timezone: timezone,
            unsubscribeToken: unsubscribeToken,
            updatedAt: updatedAt,
          );
    } catch (_) {
      late String _$failedField;
      try {
        _$failedField = 'enabledTypes';
        _enabledTypes?.build();
      } catch (e) {
        throw BuiltValueNestedFieldError(
            r'EmailPreferenceResponse', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
