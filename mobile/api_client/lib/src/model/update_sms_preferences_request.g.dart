// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'update_sms_preferences_request.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$UpdateSmsPreferencesRequest extends UpdateSmsPreferencesRequest {
  @override
  final String? language;
  @override
  final BuiltList<String> notificationTypes;

  factory _$UpdateSmsPreferencesRequest(
          [void Function(UpdateSmsPreferencesRequestBuilder)? updates]) =>
      (UpdateSmsPreferencesRequestBuilder()..update(updates))._build();

  _$UpdateSmsPreferencesRequest._(
      {this.language, required this.notificationTypes})
      : super._();
  @override
  UpdateSmsPreferencesRequest rebuild(
          void Function(UpdateSmsPreferencesRequestBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  UpdateSmsPreferencesRequestBuilder toBuilder() =>
      UpdateSmsPreferencesRequestBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is UpdateSmsPreferencesRequest &&
        language == other.language &&
        notificationTypes == other.notificationTypes;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, language.hashCode);
    _$hash = $jc(_$hash, notificationTypes.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'UpdateSmsPreferencesRequest')
          ..add('language', language)
          ..add('notificationTypes', notificationTypes))
        .toString();
  }
}

class UpdateSmsPreferencesRequestBuilder
    implements
        Builder<UpdateSmsPreferencesRequest,
            UpdateSmsPreferencesRequestBuilder> {
  _$UpdateSmsPreferencesRequest? _$v;

  String? _language;
  String? get language => _$this._language;
  set language(String? language) => _$this._language = language;

  ListBuilder<String>? _notificationTypes;
  ListBuilder<String> get notificationTypes =>
      _$this._notificationTypes ??= ListBuilder<String>();
  set notificationTypes(ListBuilder<String>? notificationTypes) =>
      _$this._notificationTypes = notificationTypes;

  UpdateSmsPreferencesRequestBuilder() {
    UpdateSmsPreferencesRequest._defaults(this);
  }

  UpdateSmsPreferencesRequestBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _language = $v.language;
      _notificationTypes = $v.notificationTypes.toBuilder();
      _$v = null;
    }
    return this;
  }

  @override
  void replace(UpdateSmsPreferencesRequest other) {
    _$v = other as _$UpdateSmsPreferencesRequest;
  }

  @override
  void update(void Function(UpdateSmsPreferencesRequestBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  UpdateSmsPreferencesRequest build() => _build();

  _$UpdateSmsPreferencesRequest _build() {
    _$UpdateSmsPreferencesRequest _$result;
    try {
      _$result = _$v ??
          _$UpdateSmsPreferencesRequest._(
            language: language,
            notificationTypes: notificationTypes.build(),
          );
    } catch (_) {
      late String _$failedField;
      try {
        _$failedField = 'notificationTypes';
        notificationTypes.build();
      } catch (e) {
        throw BuiltValueNestedFieldError(
            r'UpdateSmsPreferencesRequest', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
