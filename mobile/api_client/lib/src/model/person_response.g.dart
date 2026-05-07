// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'person_response.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$PersonResponse extends PersonResponse {
  @override
  final DateTime createdAt;
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
  @override
  final DateTime updatedAt;

  factory _$PersonResponse([void Function(PersonResponseBuilder)? updates]) =>
      (PersonResponseBuilder()..update(updates))._build();

  _$PersonResponse._(
      {required this.createdAt,
      this.email,
      this.extraData,
      required this.id,
      this.language,
      required this.name,
      required this.orgId,
      this.roles,
      this.timezone,
      required this.updatedAt})
      : super._();
  @override
  PersonResponse rebuild(void Function(PersonResponseBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  PersonResponseBuilder toBuilder() => PersonResponseBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is PersonResponse &&
        createdAt == other.createdAt &&
        email == other.email &&
        extraData == other.extraData &&
        id == other.id &&
        language == other.language &&
        name == other.name &&
        orgId == other.orgId &&
        roles == other.roles &&
        timezone == other.timezone &&
        updatedAt == other.updatedAt;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, createdAt.hashCode);
    _$hash = $jc(_$hash, email.hashCode);
    _$hash = $jc(_$hash, extraData.hashCode);
    _$hash = $jc(_$hash, id.hashCode);
    _$hash = $jc(_$hash, language.hashCode);
    _$hash = $jc(_$hash, name.hashCode);
    _$hash = $jc(_$hash, orgId.hashCode);
    _$hash = $jc(_$hash, roles.hashCode);
    _$hash = $jc(_$hash, timezone.hashCode);
    _$hash = $jc(_$hash, updatedAt.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'PersonResponse')
          ..add('createdAt', createdAt)
          ..add('email', email)
          ..add('extraData', extraData)
          ..add('id', id)
          ..add('language', language)
          ..add('name', name)
          ..add('orgId', orgId)
          ..add('roles', roles)
          ..add('timezone', timezone)
          ..add('updatedAt', updatedAt))
        .toString();
  }
}

class PersonResponseBuilder
    implements Builder<PersonResponse, PersonResponseBuilder> {
  _$PersonResponse? _$v;

  DateTime? _createdAt;
  DateTime? get createdAt => _$this._createdAt;
  set createdAt(DateTime? createdAt) => _$this._createdAt = createdAt;

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

  DateTime? _updatedAt;
  DateTime? get updatedAt => _$this._updatedAt;
  set updatedAt(DateTime? updatedAt) => _$this._updatedAt = updatedAt;

  PersonResponseBuilder() {
    PersonResponse._defaults(this);
  }

  PersonResponseBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _createdAt = $v.createdAt;
      _email = $v.email;
      _extraData = $v.extraData?.toBuilder();
      _id = $v.id;
      _language = $v.language;
      _name = $v.name;
      _orgId = $v.orgId;
      _roles = $v.roles?.toBuilder();
      _timezone = $v.timezone;
      _updatedAt = $v.updatedAt;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(PersonResponse other) {
    _$v = other as _$PersonResponse;
  }

  @override
  void update(void Function(PersonResponseBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  PersonResponse build() => _build();

  _$PersonResponse _build() {
    _$PersonResponse _$result;
    try {
      _$result = _$v ??
          _$PersonResponse._(
            createdAt: BuiltValueNullFieldError.checkNotNull(
                createdAt, r'PersonResponse', 'createdAt'),
            email: email,
            extraData: _extraData?.build(),
            id: BuiltValueNullFieldError.checkNotNull(
                id, r'PersonResponse', 'id'),
            language: language,
            name: BuiltValueNullFieldError.checkNotNull(
                name, r'PersonResponse', 'name'),
            orgId: BuiltValueNullFieldError.checkNotNull(
                orgId, r'PersonResponse', 'orgId'),
            roles: _roles?.build(),
            timezone: timezone,
            updatedAt: BuiltValueNullFieldError.checkNotNull(
                updatedAt, r'PersonResponse', 'updatedAt'),
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
            r'PersonResponse', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
