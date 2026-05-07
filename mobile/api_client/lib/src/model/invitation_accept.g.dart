// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'invitation_accept.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$InvitationAccept extends InvitationAccept {
  @override
  final String password;
  @override
  final String? timezone;

  factory _$InvitationAccept(
          [void Function(InvitationAcceptBuilder)? updates]) =>
      (InvitationAcceptBuilder()..update(updates))._build();

  _$InvitationAccept._({required this.password, this.timezone}) : super._();
  @override
  InvitationAccept rebuild(void Function(InvitationAcceptBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  InvitationAcceptBuilder toBuilder() =>
      InvitationAcceptBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is InvitationAccept &&
        password == other.password &&
        timezone == other.timezone;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, password.hashCode);
    _$hash = $jc(_$hash, timezone.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'InvitationAccept')
          ..add('password', password)
          ..add('timezone', timezone))
        .toString();
  }
}

class InvitationAcceptBuilder
    implements Builder<InvitationAccept, InvitationAcceptBuilder> {
  _$InvitationAccept? _$v;

  String? _password;
  String? get password => _$this._password;
  set password(String? password) => _$this._password = password;

  String? _timezone;
  String? get timezone => _$this._timezone;
  set timezone(String? timezone) => _$this._timezone = timezone;

  InvitationAcceptBuilder() {
    InvitationAccept._defaults(this);
  }

  InvitationAcceptBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _password = $v.password;
      _timezone = $v.timezone;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(InvitationAccept other) {
    _$v = other as _$InvitationAccept;
  }

  @override
  void update(void Function(InvitationAcceptBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  InvitationAccept build() => _build();

  _$InvitationAccept _build() {
    final _$result = _$v ??
        _$InvitationAccept._(
          password: BuiltValueNullFieldError.checkNotNull(
              password, r'InvitationAccept', 'password'),
          timezone: timezone,
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
