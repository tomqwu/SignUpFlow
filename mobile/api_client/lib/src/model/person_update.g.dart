// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'person_update.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$PersonUpdate extends PersonUpdate {
  @override
  final String? email;
  @override
  final BuiltMap<String, JsonObject?>? extraData;
  @override
  final String? language;
  @override
  final String? name;
  @override
  final BuiltList<String>? roles;
  @override
  final String? timezone;

  factory _$PersonUpdate([void Function(PersonUpdateBuilder)? updates]) =>
      (PersonUpdateBuilder()..update(updates))._build();

  _$PersonUpdate._(
      {this.email,
      this.extraData,
      this.language,
      this.name,
      this.roles,
      this.timezone})
      : super._();
  @override
  PersonUpdate rebuild(void Function(PersonUpdateBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  PersonUpdateBuilder toBuilder() => PersonUpdateBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is PersonUpdate &&
        email == other.email &&
        extraData == other.extraData &&
        language == other.language &&
        name == other.name &&
        roles == other.roles &&
        timezone == other.timezone;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, email.hashCode);
    _$hash = $jc(_$hash, extraData.hashCode);
    _$hash = $jc(_$hash, language.hashCode);
    _$hash = $jc(_$hash, name.hashCode);
    _$hash = $jc(_$hash, roles.hashCode);
    _$hash = $jc(_$hash, timezone.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'PersonUpdate')
          ..add('email', email)
          ..add('extraData', extraData)
          ..add('language', language)
          ..add('name', name)
          ..add('roles', roles)
          ..add('timezone', timezone))
        .toString();
  }
}

class PersonUpdateBuilder
    implements Builder<PersonUpdate, PersonUpdateBuilder> {
  _$PersonUpdate? _$v;

  String? _email;
  String? get email => _$this._email;
  set email(String? email) => _$this._email = email;

  MapBuilder<String, JsonObject?>? _extraData;
  MapBuilder<String, JsonObject?> get extraData =>
      _$this._extraData ??= MapBuilder<String, JsonObject?>();
  set extraData(MapBuilder<String, JsonObject?>? extraData) =>
      _$this._extraData = extraData;

  String? _language;
  String? get language => _$this._language;
  set language(String? language) => _$this._language = language;

  String? _name;
  String? get name => _$this._name;
  set name(String? name) => _$this._name = name;

  ListBuilder<String>? _roles;
  ListBuilder<String> get roles => _$this._roles ??= ListBuilder<String>();
  set roles(ListBuilder<String>? roles) => _$this._roles = roles;

  String? _timezone;
  String? get timezone => _$this._timezone;
  set timezone(String? timezone) => _$this._timezone = timezone;

  PersonUpdateBuilder() {
    PersonUpdate._defaults(this);
  }

  PersonUpdateBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _email = $v.email;
      _extraData = $v.extraData?.toBuilder();
      _language = $v.language;
      _name = $v.name;
      _roles = $v.roles?.toBuilder();
      _timezone = $v.timezone;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(PersonUpdate other) {
    _$v = other as _$PersonUpdate;
  }

  @override
  void update(void Function(PersonUpdateBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  PersonUpdate build() => _build();

  _$PersonUpdate _build() {
    _$PersonUpdate _$result;
    try {
      _$result = _$v ??
          _$PersonUpdate._(
            email: email,
            extraData: _extraData?.build(),
            language: language,
            name: name,
            roles: _roles?.build(),
            timezone: timezone,
          );
    } catch (_) {
      late String _$failedField;
      try {
        _$failedField = 'extraData';
        _extraData?.build();

        _$failedField = 'roles';
        _roles?.build();
      } catch (e) {
        throw BuiltValueNestedFieldError(
            r'PersonUpdate', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
