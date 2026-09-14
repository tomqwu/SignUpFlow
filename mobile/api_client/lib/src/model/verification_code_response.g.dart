// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'verification_code_response.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$VerificationCodeResponse extends VerificationCodeResponse {
  @override
  final String expiresAt;
  @override
  final String message;
  @override
  final String phoneNumber;

  factory _$VerificationCodeResponse(
          [void Function(VerificationCodeResponseBuilder)? updates]) =>
      (VerificationCodeResponseBuilder()..update(updates))._build();

  _$VerificationCodeResponse._(
      {required this.expiresAt,
      required this.message,
      required this.phoneNumber})
      : super._();
  @override
  VerificationCodeResponse rebuild(
          void Function(VerificationCodeResponseBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  VerificationCodeResponseBuilder toBuilder() =>
      VerificationCodeResponseBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is VerificationCodeResponse &&
        expiresAt == other.expiresAt &&
        message == other.message &&
        phoneNumber == other.phoneNumber;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, expiresAt.hashCode);
    _$hash = $jc(_$hash, message.hashCode);
    _$hash = $jc(_$hash, phoneNumber.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'VerificationCodeResponse')
          ..add('expiresAt', expiresAt)
          ..add('message', message)
          ..add('phoneNumber', phoneNumber))
        .toString();
  }
}

class VerificationCodeResponseBuilder
    implements
        Builder<VerificationCodeResponse, VerificationCodeResponseBuilder> {
  _$VerificationCodeResponse? _$v;

  String? _expiresAt;
  String? get expiresAt => _$this._expiresAt;
  set expiresAt(String? expiresAt) => _$this._expiresAt = expiresAt;

  String? _message;
  String? get message => _$this._message;
  set message(String? message) => _$this._message = message;

  String? _phoneNumber;
  String? get phoneNumber => _$this._phoneNumber;
  set phoneNumber(String? phoneNumber) => _$this._phoneNumber = phoneNumber;

  VerificationCodeResponseBuilder() {
    VerificationCodeResponse._defaults(this);
  }

  VerificationCodeResponseBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _expiresAt = $v.expiresAt;
      _message = $v.message;
      _phoneNumber = $v.phoneNumber;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(VerificationCodeResponse other) {
    _$v = other as _$VerificationCodeResponse;
  }

  @override
  void update(void Function(VerificationCodeResponseBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  VerificationCodeResponse build() => _build();

  _$VerificationCodeResponse _build() {
    final _$result = _$v ??
        _$VerificationCodeResponse._(
          expiresAt: BuiltValueNullFieldError.checkNotNull(
              expiresAt, r'VerificationCodeResponse', 'expiresAt'),
          message: BuiltValueNullFieldError.checkNotNull(
              message, r'VerificationCodeResponse', 'message'),
          phoneNumber: BuiltValueNullFieldError.checkNotNull(
              phoneNumber, r'VerificationCodeResponse', 'phoneNumber'),
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
