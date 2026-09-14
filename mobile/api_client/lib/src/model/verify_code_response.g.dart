// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'verify_code_response.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$VerifyCodeResponse extends VerifyCodeResponse {
  @override
  final String message;
  @override
  final String phoneNumber;
  @override
  final bool verified;

  factory _$VerifyCodeResponse(
          [void Function(VerifyCodeResponseBuilder)? updates]) =>
      (VerifyCodeResponseBuilder()..update(updates))._build();

  _$VerifyCodeResponse._(
      {required this.message,
      required this.phoneNumber,
      required this.verified})
      : super._();
  @override
  VerifyCodeResponse rebuild(
          void Function(VerifyCodeResponseBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  VerifyCodeResponseBuilder toBuilder() =>
      VerifyCodeResponseBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is VerifyCodeResponse &&
        message == other.message &&
        phoneNumber == other.phoneNumber &&
        verified == other.verified;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, message.hashCode);
    _$hash = $jc(_$hash, phoneNumber.hashCode);
    _$hash = $jc(_$hash, verified.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'VerifyCodeResponse')
          ..add('message', message)
          ..add('phoneNumber', phoneNumber)
          ..add('verified', verified))
        .toString();
  }
}

class VerifyCodeResponseBuilder
    implements Builder<VerifyCodeResponse, VerifyCodeResponseBuilder> {
  _$VerifyCodeResponse? _$v;

  String? _message;
  String? get message => _$this._message;
  set message(String? message) => _$this._message = message;

  String? _phoneNumber;
  String? get phoneNumber => _$this._phoneNumber;
  set phoneNumber(String? phoneNumber) => _$this._phoneNumber = phoneNumber;

  bool? _verified;
  bool? get verified => _$this._verified;
  set verified(bool? verified) => _$this._verified = verified;

  VerifyCodeResponseBuilder() {
    VerifyCodeResponse._defaults(this);
  }

  VerifyCodeResponseBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _message = $v.message;
      _phoneNumber = $v.phoneNumber;
      _verified = $v.verified;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(VerifyCodeResponse other) {
    _$v = other as _$VerifyCodeResponse;
  }

  @override
  void update(void Function(VerifyCodeResponseBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  VerifyCodeResponse build() => _build();

  _$VerifyCodeResponse _build() {
    final _$result = _$v ??
        _$VerifyCodeResponse._(
          message: BuiltValueNullFieldError.checkNotNull(
              message, r'VerifyCodeResponse', 'message'),
          phoneNumber: BuiltValueNullFieldError.checkNotNull(
              phoneNumber, r'VerifyCodeResponse', 'phoneNumber'),
          verified: BuiltValueNullFieldError.checkNotNull(
              verified, r'VerifyCodeResponse', 'verified'),
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
