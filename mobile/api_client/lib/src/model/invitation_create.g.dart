// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'invitation_create.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$InvitationCreate extends InvitationCreate {
  @override
  final String email;
  @override
  final String name;
  @override
  final BuiltList<String> roles;

  factory _$InvitationCreate(
          [void Function(InvitationCreateBuilder)? updates]) =>
      (InvitationCreateBuilder()..update(updates))._build();

  _$InvitationCreate._(
      {required this.email, required this.name, required this.roles})
      : super._();
  @override
  InvitationCreate rebuild(void Function(InvitationCreateBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  InvitationCreateBuilder toBuilder() =>
      InvitationCreateBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is InvitationCreate &&
        email == other.email &&
        name == other.name &&
        roles == other.roles;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, email.hashCode);
    _$hash = $jc(_$hash, name.hashCode);
    _$hash = $jc(_$hash, roles.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'InvitationCreate')
          ..add('email', email)
          ..add('name', name)
          ..add('roles', roles))
        .toString();
  }
}

class InvitationCreateBuilder
    implements Builder<InvitationCreate, InvitationCreateBuilder> {
  _$InvitationCreate? _$v;

  String? _email;
  String? get email => _$this._email;
  set email(String? email) => _$this._email = email;

  String? _name;
  String? get name => _$this._name;
  set name(String? name) => _$this._name = name;

  ListBuilder<String>? _roles;
  ListBuilder<String> get roles => _$this._roles ??= ListBuilder<String>();
  set roles(ListBuilder<String>? roles) => _$this._roles = roles;

  InvitationCreateBuilder() {
    InvitationCreate._defaults(this);
  }

  InvitationCreateBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _email = $v.email;
      _name = $v.name;
      _roles = $v.roles.toBuilder();
      _$v = null;
    }
    return this;
  }

  @override
  void replace(InvitationCreate other) {
    _$v = other as _$InvitationCreate;
  }

  @override
  void update(void Function(InvitationCreateBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  InvitationCreate build() => _build();

  _$InvitationCreate _build() {
    _$InvitationCreate _$result;
    try {
      _$result = _$v ??
          _$InvitationCreate._(
            email: BuiltValueNullFieldError.checkNotNull(
                email, r'InvitationCreate', 'email'),
            name: BuiltValueNullFieldError.checkNotNull(
                name, r'InvitationCreate', 'name'),
            roles: roles.build(),
          );
    } catch (_) {
      late String _$failedField;
      try {
        _$failedField = 'roles';
        roles.build();
      } catch (e) {
        throw BuiltValueNestedFieldError(
            r'InvitationCreate', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
