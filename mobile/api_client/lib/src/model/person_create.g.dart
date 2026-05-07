// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'person_create.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$PersonCreate extends PersonCreate {
  @override
  final String? email;
  @override
  final BuiltMap<String, JsonObject?>? extraData;
  @override
  final String id;
  @override
  final String? language;
  @override
  final String name;
  @override
  final String orgId;
  @override
  final BuiltList<String>? roles;
  @override
  final String? timezone;

  factory _$PersonCreate([void Function(PersonCreateBuilder)? updates]) =>
      (PersonCreateBuilder()..update(updates))._build();

  _$PersonCreate._(
      {this.email,
      this.extraData,
      required this.id,
      this.language,
      required this.name,
      required this.orgId,
      this.roles,
      this.timezone})
      : super._();
  @override
  PersonCreate rebuild(void Function(PersonCreateBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  PersonCreateBuilder toBuilder() => PersonCreateBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is PersonCreate &&
        email == other.email &&
        extraData == other.extraData &&
        id == other.id &&
        language == other.language &&
        name == other.name &&
        orgId == other.orgId &&
        roles == other.roles &&
        timezone == other.timezone;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, email.hashCode);
    _$hash = $jc(_$hash, extraData.hashCode);
    _$hash = $jc(_$hash, id.hashCode);
    _$hash = $jc(_$hash, language.hashCode);
    _$hash = $jc(_$hash, name.hashCode);
    _$hash = $jc(_$hash, orgId.hashCode);
    _$hash = $jc(_$hash, roles.hashCode);
    _$hash = $jc(_$hash, timezone.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'PersonCreate')
          ..add('email', email)
          ..add('extraData', extraData)
          ..add('id', id)
          ..add('language', language)
          ..add('name', name)
          ..add('orgId', orgId)
          ..add('roles', roles)
          ..add('timezone', timezone))
        .toString();
  }
}

class PersonCreateBuilder
    implements Builder<PersonCreate, PersonCreateBuilder> {
  _$PersonCreate? _$v;

  String? _email;
  String? get email => _$this._email;
  set email(String? email) => _$this._email = email;

  MapBuilder<String, JsonObject?>? _extraData;
  MapBuilder<String, JsonObject?> get extraData =>
      _$this._extraData ??= MapBuilder<String, JsonObject?>();
  set extraData(MapBuilder<String, JsonObject?>? extraData) =>
      _$this._extraData = extraData;

  String? _id;
  String? get id => _$this._id;
  set id(String? id) => _$this._id = id;

  String? _language;
  String? get language => _$this._language;
  set language(String? language) => _$this._language = language;

  String? _name;
  String? get name => _$this._name;
  set name(String? name) => _$this._name = name;

  String? _orgId;
  String? get orgId => _$this._orgId;
  set orgId(String? orgId) => _$this._orgId = orgId;

  ListBuilder<String>? _roles;
  ListBuilder<String> get roles => _$this._roles ??= ListBuilder<String>();
  set roles(ListBuilder<String>? roles) => _$this._roles = roles;

  String? _timezone;
  String? get timezone => _$this._timezone;
  set timezone(String? timezone) => _$this._timezone = timezone;

  PersonCreateBuilder() {
    PersonCreate._defaults(this);
  }

  PersonCreateBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _email = $v.email;
      _extraData = $v.extraData?.toBuilder();
      _id = $v.id;
      _language = $v.language;
      _name = $v.name;
      _orgId = $v.orgId;
      _roles = $v.roles?.toBuilder();
      _timezone = $v.timezone;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(PersonCreate other) {
    _$v = other as _$PersonCreate;
  }

  @override
  void update(void Function(PersonCreateBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  PersonCreate build() => _build();

  _$PersonCreate _build() {
    _$PersonCreate _$result;
    try {
      _$result = _$v ??
          _$PersonCreate._(
            email: email,
            extraData: _extraData?.build(),
            id: BuiltValueNullFieldError.checkNotNull(
                id, r'PersonCreate', 'id'),
            language: language,
            name: BuiltValueNullFieldError.checkNotNull(
                name, r'PersonCreate', 'name'),
            orgId: BuiltValueNullFieldError.checkNotNull(
                orgId, r'PersonCreate', 'orgId'),
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
            r'PersonCreate', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
