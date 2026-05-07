// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'invitation_accept_response.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$InvitationAcceptResponse extends InvitationAcceptResponse {
  @override
  final String email;
  @override
  final String message;
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

  factory _$InvitationAcceptResponse(
          [void Function(InvitationAcceptResponseBuilder)? updates]) =>
      (InvitationAcceptResponseBuilder()..update(updates))._build();

  _$InvitationAcceptResponse._(
      {required this.email,
      required this.message,
      required this.name,
      required this.orgId,
      required this.personId,
      required this.roles,
      required this.timezone,
      required this.token})
      : super._();
  @override
  InvitationAcceptResponse rebuild(
          void Function(InvitationAcceptResponseBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  InvitationAcceptResponseBuilder toBuilder() =>
      InvitationAcceptResponseBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is InvitationAcceptResponse &&
        email == other.email &&
        message == other.message &&
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
    _$hash = $jc(_$hash, message.hashCode);
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
    return (newBuiltValueToStringHelper(r'InvitationAcceptResponse')
          ..add('email', email)
          ..add('message', message)
          ..add('name', name)
          ..add('orgId', orgId)
          ..add('personId', personId)
          ..add('roles', roles)
          ..add('timezone', timezone)
          ..add('token', token))
        .toString();
  }
}

class InvitationAcceptResponseBuilder
    implements
        Builder<InvitationAcceptResponse, InvitationAcceptResponseBuilder> {
  _$InvitationAcceptResponse? _$v;

  String? _email;
  String? get email => _$this._email;
  set email(String? email) => _$this._email = email;

  String? _message;
  String? get message => _$this._message;
  set message(String? message) => _$this._message = message;

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

  InvitationAcceptResponseBuilder() {
    InvitationAcceptResponse._defaults(this);
  }

  InvitationAcceptResponseBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _email = $v.email;
      _message = $v.message;
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
  void replace(InvitationAcceptResponse other) {
    _$v = other as _$InvitationAcceptResponse;
  }

  @override
  void update(void Function(InvitationAcceptResponseBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  InvitationAcceptResponse build() => _build();

  _$InvitationAcceptResponse _build() {
    _$InvitationAcceptResponse _$result;
    try {
      _$result = _$v ??
          _$InvitationAcceptResponse._(
            email: BuiltValueNullFieldError.checkNotNull(
                email, r'InvitationAcceptResponse', 'email'),
            message: BuiltValueNullFieldError.checkNotNull(
                message, r'InvitationAcceptResponse', 'message'),
            name: BuiltValueNullFieldError.checkNotNull(
                name, r'InvitationAcceptResponse', 'name'),
            orgId: BuiltValueNullFieldError.checkNotNull(
                orgId, r'InvitationAcceptResponse', 'orgId'),
            personId: BuiltValueNullFieldError.checkNotNull(
                personId, r'InvitationAcceptResponse', 'personId'),
            roles: roles.build(),
            timezone: BuiltValueNullFieldError.checkNotNull(
                timezone, r'InvitationAcceptResponse', 'timezone'),
            token: BuiltValueNullFieldError.checkNotNull(
                token, r'InvitationAcceptResponse', 'token'),
          );
    } catch (_) {
      late String _$failedField;
      try {
        _$failedField = 'roles';
        roles.build();
      } catch (e) {
        throw BuiltValueNestedFieldError(
            r'InvitationAcceptResponse', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
