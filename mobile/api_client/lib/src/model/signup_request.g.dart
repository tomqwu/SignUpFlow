// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'signup_request.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$SignupRequest extends SignupRequest {
  @override
  final String email;
  @override
  final String? language;
  @override
  final String name;
  @override
  final String orgId;
  @override
  final String orgName;
  @override
  final String password;
  @override
  final String? region;
  @override
  final String? timezone;

  factory _$SignupRequest([void Function(SignupRequestBuilder)? updates]) =>
      (SignupRequestBuilder()..update(updates))._build();

  _$SignupRequest._(
      {required this.email,
      this.language,
      required this.name,
      required this.orgId,
      required this.orgName,
      required this.password,
      this.region,
      this.timezone})
      : super._();
  @override
  SignupRequest rebuild(void Function(SignupRequestBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  SignupRequestBuilder toBuilder() => SignupRequestBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is SignupRequest &&
        email == other.email &&
        language == other.language &&
        name == other.name &&
        orgId == other.orgId &&
        orgName == other.orgName &&
        password == other.password &&
        region == other.region &&
        timezone == other.timezone;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, email.hashCode);
    _$hash = $jc(_$hash, language.hashCode);
    _$hash = $jc(_$hash, name.hashCode);
    _$hash = $jc(_$hash, orgId.hashCode);
    _$hash = $jc(_$hash, orgName.hashCode);
    _$hash = $jc(_$hash, password.hashCode);
    _$hash = $jc(_$hash, region.hashCode);
    _$hash = $jc(_$hash, timezone.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'SignupRequest')
          ..add('email', email)
          ..add('language', language)
          ..add('name', name)
          ..add('orgId', orgId)
          ..add('orgName', orgName)
          ..add('password', password)
          ..add('region', region)
          ..add('timezone', timezone))
        .toString();
  }
}

class SignupRequestBuilder
    implements Builder<SignupRequest, SignupRequestBuilder> {
  _$SignupRequest? _$v;

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

  String? _orgName;
  String? get orgName => _$this._orgName;
  set orgName(String? orgName) => _$this._orgName = orgName;

  String? _password;
  String? get password => _$this._password;
  set password(String? password) => _$this._password = password;

  String? _region;
  String? get region => _$this._region;
  set region(String? region) => _$this._region = region;

  String? _timezone;
  String? get timezone => _$this._timezone;
  set timezone(String? timezone) => _$this._timezone = timezone;

  SignupRequestBuilder() {
    SignupRequest._defaults(this);
  }

  SignupRequestBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _email = $v.email;
      _language = $v.language;
      _name = $v.name;
      _orgId = $v.orgId;
      _orgName = $v.orgName;
      _password = $v.password;
      _region = $v.region;
      _timezone = $v.timezone;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(SignupRequest other) {
    _$v = other as _$SignupRequest;
  }

  @override
  void update(void Function(SignupRequestBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  SignupRequest build() => _build();

  _$SignupRequest _build() {
    final _$result = _$v ??
        _$SignupRequest._(
          email: BuiltValueNullFieldError.checkNotNull(
              email, r'SignupRequest', 'email'),
          language: language,
          name: BuiltValueNullFieldError.checkNotNull(
              name, r'SignupRequest', 'name'),
          orgId: BuiltValueNullFieldError.checkNotNull(
              orgId, r'SignupRequest', 'orgId'),
          orgName: BuiltValueNullFieldError.checkNotNull(
              orgName, r'SignupRequest', 'orgName'),
          password: BuiltValueNullFieldError.checkNotNull(
              password, r'SignupRequest', 'password'),
          region: region,
          timezone: timezone,
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
