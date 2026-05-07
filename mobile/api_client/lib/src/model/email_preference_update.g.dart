// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'email_preference_update.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$EmailPreferenceUpdate extends EmailPreferenceUpdate {
  @override
  final int? digestHour;
  @override
  final BuiltList<String>? enabledTypes;
  @override
  final String? frequency;
  @override
  final String? language;
  @override
  final String? timezone;

  factory _$EmailPreferenceUpdate(
          [void Function(EmailPreferenceUpdateBuilder)? updates]) =>
      (EmailPreferenceUpdateBuilder()..update(updates))._build();

  _$EmailPreferenceUpdate._(
      {this.digestHour,
      this.enabledTypes,
      this.frequency,
      this.language,
      this.timezone})
      : super._();
  @override
  EmailPreferenceUpdate rebuild(
          void Function(EmailPreferenceUpdateBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  EmailPreferenceUpdateBuilder toBuilder() =>
      EmailPreferenceUpdateBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is EmailPreferenceUpdate &&
        digestHour == other.digestHour &&
        enabledTypes == other.enabledTypes &&
        frequency == other.frequency &&
        language == other.language &&
        timezone == other.timezone;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, digestHour.hashCode);
    _$hash = $jc(_$hash, enabledTypes.hashCode);
    _$hash = $jc(_$hash, frequency.hashCode);
    _$hash = $jc(_$hash, language.hashCode);
    _$hash = $jc(_$hash, timezone.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'EmailPreferenceUpdate')
          ..add('digestHour', digestHour)
          ..add('enabledTypes', enabledTypes)
          ..add('frequency', frequency)
          ..add('language', language)
          ..add('timezone', timezone))
        .toString();
  }
}

class EmailPreferenceUpdateBuilder
    implements Builder<EmailPreferenceUpdate, EmailPreferenceUpdateBuilder> {
  _$EmailPreferenceUpdate? _$v;

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

  String? _language;
  String? get language => _$this._language;
  set language(String? language) => _$this._language = language;

  String? _timezone;
  String? get timezone => _$this._timezone;
  set timezone(String? timezone) => _$this._timezone = timezone;

  EmailPreferenceUpdateBuilder() {
    EmailPreferenceUpdate._defaults(this);
  }

  EmailPreferenceUpdateBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _digestHour = $v.digestHour;
      _enabledTypes = $v.enabledTypes?.toBuilder();
      _frequency = $v.frequency;
      _language = $v.language;
      _timezone = $v.timezone;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(EmailPreferenceUpdate other) {
    _$v = other as _$EmailPreferenceUpdate;
  }

  @override
  void update(void Function(EmailPreferenceUpdateBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  EmailPreferenceUpdate build() => _build();

  _$EmailPreferenceUpdate _build() {
    _$EmailPreferenceUpdate _$result;
    try {
      _$result = _$v ??
          _$EmailPreferenceUpdate._(
            digestHour: digestHour,
            enabledTypes: _enabledTypes?.build(),
            frequency: frequency,
            language: language,
            timezone: timezone,
          );
    } catch (_) {
      late String _$failedField;
      try {
        _$failedField = 'enabledTypes';
        _enabledTypes?.build();
      } catch (e) {
        throw BuiltValueNestedFieldError(
            r'EmailPreferenceUpdate', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
