// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'invitation_response.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$InvitationResponse extends InvitationResponse {
  @override
  final DateTime? acceptedAt;
  @override
  final DateTime createdAt;
  @override
  final String email;
  @override
  final DateTime expiresAt;
  @override
  final String id;
  @override
  final String invitedBy;
  @override
  final String name;
  @override
  final String orgId;
  @override
  final BuiltList<String> roles;
  @override
  final String status;
  @override
  final String token;

  factory _$InvitationResponse(
          [void Function(InvitationResponseBuilder)? updates]) =>
      (InvitationResponseBuilder()..update(updates))._build();

  _$InvitationResponse._(
      {this.acceptedAt,
      required this.createdAt,
      required this.email,
      required this.expiresAt,
      required this.id,
      required this.invitedBy,
      required this.name,
      required this.orgId,
      required this.roles,
      required this.status,
      required this.token})
      : super._();
  @override
  InvitationResponse rebuild(
          void Function(InvitationResponseBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  InvitationResponseBuilder toBuilder() =>
      InvitationResponseBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is InvitationResponse &&
        acceptedAt == other.acceptedAt &&
        createdAt == other.createdAt &&
        email == other.email &&
        expiresAt == other.expiresAt &&
        id == other.id &&
        invitedBy == other.invitedBy &&
        name == other.name &&
        orgId == other.orgId &&
        roles == other.roles &&
        status == other.status &&
        token == other.token;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, acceptedAt.hashCode);
    _$hash = $jc(_$hash, createdAt.hashCode);
    _$hash = $jc(_$hash, email.hashCode);
    _$hash = $jc(_$hash, expiresAt.hashCode);
    _$hash = $jc(_$hash, id.hashCode);
    _$hash = $jc(_$hash, invitedBy.hashCode);
    _$hash = $jc(_$hash, name.hashCode);
    _$hash = $jc(_$hash, orgId.hashCode);
    _$hash = $jc(_$hash, roles.hashCode);
    _$hash = $jc(_$hash, status.hashCode);
    _$hash = $jc(_$hash, token.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'InvitationResponse')
          ..add('acceptedAt', acceptedAt)
          ..add('createdAt', createdAt)
          ..add('email', email)
          ..add('expiresAt', expiresAt)
          ..add('id', id)
          ..add('invitedBy', invitedBy)
          ..add('name', name)
          ..add('orgId', orgId)
          ..add('roles', roles)
          ..add('status', status)
          ..add('token', token))
        .toString();
  }
}

class InvitationResponseBuilder
    implements Builder<InvitationResponse, InvitationResponseBuilder> {
  _$InvitationResponse? _$v;

  DateTime? _acceptedAt;
  DateTime? get acceptedAt => _$this._acceptedAt;
  set acceptedAt(DateTime? acceptedAt) => _$this._acceptedAt = acceptedAt;

  DateTime? _createdAt;
  DateTime? get createdAt => _$this._createdAt;
  set createdAt(DateTime? createdAt) => _$this._createdAt = createdAt;

  String? _email;
  String? get email => _$this._email;
  set email(String? email) => _$this._email = email;

  DateTime? _expiresAt;
  DateTime? get expiresAt => _$this._expiresAt;
  set expiresAt(DateTime? expiresAt) => _$this._expiresAt = expiresAt;

  String? _id;
  String? get id => _$this._id;
  set id(String? id) => _$this._id = id;

  String? _invitedBy;
  String? get invitedBy => _$this._invitedBy;
  set invitedBy(String? invitedBy) => _$this._invitedBy = invitedBy;

  String? _name;
  String? get name => _$this._name;
  set name(String? name) => _$this._name = name;

  String? _orgId;
  String? get orgId => _$this._orgId;
  set orgId(String? orgId) => _$this._orgId = orgId;

  ListBuilder<String>? _roles;
  ListBuilder<String> get roles => _$this._roles ??= ListBuilder<String>();
  set roles(ListBuilder<String>? roles) => _$this._roles = roles;

  String? _status;
  String? get status => _$this._status;
  set status(String? status) => _$this._status = status;

  String? _token;
  String? get token => _$this._token;
  set token(String? token) => _$this._token = token;

  InvitationResponseBuilder() {
    InvitationResponse._defaults(this);
  }

  InvitationResponseBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _acceptedAt = $v.acceptedAt;
      _createdAt = $v.createdAt;
      _email = $v.email;
      _expiresAt = $v.expiresAt;
      _id = $v.id;
      _invitedBy = $v.invitedBy;
      _name = $v.name;
      _orgId = $v.orgId;
      _roles = $v.roles.toBuilder();
      _status = $v.status;
      _token = $v.token;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(InvitationResponse other) {
    _$v = other as _$InvitationResponse;
  }

  @override
  void update(void Function(InvitationResponseBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  InvitationResponse build() => _build();

  _$InvitationResponse _build() {
    _$InvitationResponse _$result;
    try {
      _$result = _$v ??
          _$InvitationResponse._(
            acceptedAt: acceptedAt,
            createdAt: BuiltValueNullFieldError.checkNotNull(
                createdAt, r'InvitationResponse', 'createdAt'),
            email: BuiltValueNullFieldError.checkNotNull(
                email, r'InvitationResponse', 'email'),
            expiresAt: BuiltValueNullFieldError.checkNotNull(
                expiresAt, r'InvitationResponse', 'expiresAt'),
            id: BuiltValueNullFieldError.checkNotNull(
                id, r'InvitationResponse', 'id'),
            invitedBy: BuiltValueNullFieldError.checkNotNull(
                invitedBy, r'InvitationResponse', 'invitedBy'),
            name: BuiltValueNullFieldError.checkNotNull(
                name, r'InvitationResponse', 'name'),
            orgId: BuiltValueNullFieldError.checkNotNull(
                orgId, r'InvitationResponse', 'orgId'),
            roles: roles.build(),
            status: BuiltValueNullFieldError.checkNotNull(
                status, r'InvitationResponse', 'status'),
            token: BuiltValueNullFieldError.checkNotNull(
                token, r'InvitationResponse', 'token'),
          );
    } catch (_) {
      late String _$failedField;
      try {
        _$failedField = 'roles';
        roles.build();
      } catch (e) {
        throw BuiltValueNestedFieldError(
            r'InvitationResponse', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
