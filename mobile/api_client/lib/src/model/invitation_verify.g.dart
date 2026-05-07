// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'invitation_verify.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$InvitationVerify extends InvitationVerify {
  @override
  final InvitationResponse? invitation;
  @override
  final String? message;
  @override
  final bool valid;

  factory _$InvitationVerify(
          [void Function(InvitationVerifyBuilder)? updates]) =>
      (InvitationVerifyBuilder()..update(updates))._build();

  _$InvitationVerify._({this.invitation, this.message, required this.valid})
      : super._();
  @override
  InvitationVerify rebuild(void Function(InvitationVerifyBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  InvitationVerifyBuilder toBuilder() =>
      InvitationVerifyBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is InvitationVerify &&
        invitation == other.invitation &&
        message == other.message &&
        valid == other.valid;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, invitation.hashCode);
    _$hash = $jc(_$hash, message.hashCode);
    _$hash = $jc(_$hash, valid.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'InvitationVerify')
          ..add('invitation', invitation)
          ..add('message', message)
          ..add('valid', valid))
        .toString();
  }
}

class InvitationVerifyBuilder
    implements Builder<InvitationVerify, InvitationVerifyBuilder> {
  _$InvitationVerify? _$v;

  InvitationResponseBuilder? _invitation;
  InvitationResponseBuilder get invitation =>
      _$this._invitation ??= InvitationResponseBuilder();
  set invitation(InvitationResponseBuilder? invitation) =>
      _$this._invitation = invitation;

  String? _message;
  String? get message => _$this._message;
  set message(String? message) => _$this._message = message;

  bool? _valid;
  bool? get valid => _$this._valid;
  set valid(bool? valid) => _$this._valid = valid;

  InvitationVerifyBuilder() {
    InvitationVerify._defaults(this);
  }

  InvitationVerifyBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _invitation = $v.invitation?.toBuilder();
      _message = $v.message;
      _valid = $v.valid;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(InvitationVerify other) {
    _$v = other as _$InvitationVerify;
  }

  @override
  void update(void Function(InvitationVerifyBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  InvitationVerify build() => _build();

  _$InvitationVerify _build() {
    _$InvitationVerify _$result;
    try {
      _$result = _$v ??
          _$InvitationVerify._(
            invitation: _invitation?.build(),
            message: message,
            valid: BuiltValueNullFieldError.checkNotNull(
                valid, r'InvitationVerify', 'valid'),
          );
    } catch (_) {
      late String _$failedField;
      try {
        _$failedField = 'invitation';
        _invitation?.build();
      } catch (e) {
        throw BuiltValueNestedFieldError(
            r'InvitationVerify', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
