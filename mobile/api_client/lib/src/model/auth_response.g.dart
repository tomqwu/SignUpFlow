// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'auth_response.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$AuthResponse extends AuthResponse {
  @override
  final String email;
  @override
  final String language;
  @override
  final String name;
  @override
  final String orgId;
  @override
  final String personId;
  @override
  final BuiltList<String> roles;
  @override
  final String timezone;
  @override
  final String token;

  factory _$AuthResponse([void Function(AuthResponseBuilder)? updates]) =>
      (AuthResponseBuilder()..update(updates))._build();

  _$AuthResponse._(
      {required this.email,
      required this.language,
      required this.name,
      required this.orgId,
      required this.personId,
      required this.roles,
      required this.timezone,
      required this.token})
      : super._();
  @override
  AuthResponse rebuild(void Function(AuthResponseBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  AuthResponseBuilder toBuilder() => AuthResponseBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is AuthResponse &&
        email == other.email &&
        language == other.language &&
        name == other.name &&
        orgId == other.orgId &&
        personId == other.personId &&
        roles == other.roles &&
        timezone == other.timezone &&
        token == other.token;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, email.hashCode);
    _$hash = $jc(_$hash, language.hashCode);
    _$hash = $jc(_$hash, name.hashCode);
    _$hash = $jc(_$hash, orgId.hashCode);
    _$hash = $jc(_$hash, personId.hashCode);
    _$hash = $jc(_$hash, roles.hashCode);
    _$hash = $jc(_$hash, timezone.hashCode);
    _$hash = $jc(_$hash, token.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'AuthResponse')
          ..add('email', email)
          ..add('language', language)
          ..add('name', name)
          ..add('orgId', orgId)
          ..add('personId', personId)
          ..add('roles', roles)
          ..add('timezone', timezone)
          ..add('token', token))
        .toString();
  }
}

class AuthResponseBuilder
    implements Builder<AuthResponse, AuthResponseBuilder> {
  _$AuthResponse? _$v;

  String? _email;
  String? get email => _$this._email;
  set email(String? email) => _$this._email = email;

  String? _language;
  String? get language => _$this._language;
  set language(String? language) => _$this._language = language;

  String? _name;
  String? get name => _$this._name;
  set name(String? name) => _$this._name = name;

  String? _orgId;
  String? get orgId => _$this._orgId;
  set orgId(String? orgId) => _$this._orgId = orgId;

  String? _personId;
  String? get personId => _$this._personId;
  set personId(String? personId) => _$this._personId = personId;

  ListBuilder<String>? _roles;
  ListBuilder<String> get roles => _$this._roles ??= ListBuilder<String>();
  set roles(ListBuilder<String>? roles) => _$this._roles = roles;

  String? _timezone;
  String? get timezone => _$this._timezone;
  set timezone(String? timezone) => _$this._timezone = timezone;

  String? _token;
  String? get token => _$this._token;
  set token(String? token) => _$this._token = token;

  AuthResponseBuilder() {
    AuthResponse._defaults(this);
  }

  AuthResponseBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _email = $v.email;
      _language = $v.language;
      _name = $v.name;
      _orgId = $v.orgId;
      _personId = $v.personId;
      _roles = $v.roles.toBuilder();
      _timezone = $v.timezone;
      _token = $v.token;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(AuthResponse other) {
    _$v = other as _$AuthResponse;
  }

  @override
  void update(void Function(AuthResponseBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  AuthResponse build() => _build();

  _$AuthResponse _build() {
    _$AuthResponse _$result;
    try {
      _$result = _$v ??
          _$AuthResponse._(
            email: BuiltValueNullFieldError.checkNotNull(
                email, r'AuthResponse', 'email'),
            language: BuiltValueNullFieldError.checkNotNull(
                language, r'AuthResponse', 'language'),
            name: BuiltValueNullFieldError.checkNotNull(
                name, r'AuthResponse', 'name'),
            orgId: BuiltValueNullFieldError.checkNotNull(
                orgId, r'AuthResponse', 'orgId'),
            personId: BuiltValueNullFieldError.checkNotNull(
                personId, r'AuthResponse', 'personId'),
            roles: roles.build(),
            timezone: BuiltValueNullFieldError.checkNotNull(
                timezone, r'AuthResponse', 'timezone'),
            token: BuiltValueNullFieldError.checkNotNull(
                token, r'AuthResponse', 'token'),
          );
    } catch (_) {
      late String _$failedField;
      try {
        _$failedField = 'roles';
        roles.build();
      } catch (e) {
        throw BuiltValueNestedFieldError(
            r'AuthResponse', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
