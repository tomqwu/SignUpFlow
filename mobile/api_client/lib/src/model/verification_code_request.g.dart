// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'verification_code_request.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$VerificationCodeRequest extends VerificationCodeRequest {
  @override
  final String personId;
  @override
  final String phoneNumber;

  factory _$VerificationCodeRequest(
          [void Function(VerificationCodeRequestBuilder)? updates]) =>
      (VerificationCodeRequestBuilder()..update(updates))._build();

  _$VerificationCodeRequest._(
      {required this.personId, required this.phoneNumber})
      : super._();
  @override
  VerificationCodeRequest rebuild(
          void Function(VerificationCodeRequestBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  VerificationCodeRequestBuilder toBuilder() =>
      VerificationCodeRequestBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is VerificationCodeRequest &&
        personId == other.personId &&
        phoneNumber == other.phoneNumber;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, personId.hashCode);
    _$hash = $jc(_$hash, phoneNumber.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'VerificationCodeRequest')
          ..add('personId', personId)
          ..add('phoneNumber', phoneNumber))
        .toString();
  }
}

class VerificationCodeRequestBuilder
    implements
        Builder<VerificationCodeRequest, VerificationCodeRequestBuilder> {
  _$VerificationCodeRequest? _$v;

  String? _personId;
  String? get personId => _$this._personId;
  set personId(String? personId) => _$this._personId = personId;

  String? _phoneNumber;
  String? get phoneNumber => _$this._phoneNumber;
  set phoneNumber(String? phoneNumber) => _$this._phoneNumber = phoneNumber;

  VerificationCodeRequestBuilder() {
    VerificationCodeRequest._defaults(this);
  }

  VerificationCodeRequestBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _personId = $v.personId;
      _phoneNumber = $v.phoneNumber;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(VerificationCodeRequest other) {
    _$v = other as _$VerificationCodeRequest;
  }

  @override
  void update(void Function(VerificationCodeRequestBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  VerificationCodeRequest build() => _build();

  _$VerificationCodeRequest _build() {
    final _$result = _$v ??
        _$VerificationCodeRequest._(
          personId: BuiltValueNullFieldError.checkNotNull(
              personId, r'VerificationCodeRequest', 'personId'),
          phoneNumber: BuiltValueNullFieldError.checkNotNull(
              phoneNumber, r'VerificationCodeRequest', 'phoneNumber'),
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
