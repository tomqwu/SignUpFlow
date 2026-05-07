// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'password_reset_confirm.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$PasswordResetConfirm extends PasswordResetConfirm {
  @override
  final String newPassword;
  @override
  final String token;

  factory _$PasswordResetConfirm(
          [void Function(PasswordResetConfirmBuilder)? updates]) =>
      (PasswordResetConfirmBuilder()..update(updates))._build();

  _$PasswordResetConfirm._({required this.newPassword, required this.token})
      : super._();
  @override
  PasswordResetConfirm rebuild(
          void Function(PasswordResetConfirmBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  PasswordResetConfirmBuilder toBuilder() =>
      PasswordResetConfirmBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is PasswordResetConfirm &&
        newPassword == other.newPassword &&
        token == other.token;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, newPassword.hashCode);
    _$hash = $jc(_$hash, token.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'PasswordResetConfirm')
          ..add('newPassword', newPassword)
          ..add('token', token))
        .toString();
  }
}

class PasswordResetConfirmBuilder
    implements Builder<PasswordResetConfirm, PasswordResetConfirmBuilder> {
  _$PasswordResetConfirm? _$v;

  String? _newPassword;
  String? get newPassword => _$this._newPassword;
  set newPassword(String? newPassword) => _$this._newPassword = newPassword;

  String? _token;
  String? get token => _$this._token;
  set token(String? token) => _$this._token = token;

  PasswordResetConfirmBuilder() {
    PasswordResetConfirm._defaults(this);
  }

  PasswordResetConfirmBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _newPassword = $v.newPassword;
      _token = $v.token;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(PasswordResetConfirm other) {
    _$v = other as _$PasswordResetConfirm;
  }

  @override
  void update(void Function(PasswordResetConfirmBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  PasswordResetConfirm build() => _build();

  _$PasswordResetConfirm _build() {
    final _$result = _$v ??
        _$PasswordResetConfirm._(
          newPassword: BuiltValueNullFieldError.checkNotNull(
              newPassword, r'PasswordResetConfirm', 'newPassword'),
          token: BuiltValueNullFieldError.checkNotNull(
              token, r'PasswordResetConfirm', 'token'),
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
