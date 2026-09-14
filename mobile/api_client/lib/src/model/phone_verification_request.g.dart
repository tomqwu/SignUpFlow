// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'phone_verification_request.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$PhoneVerificationRequest extends PhoneVerificationRequest {
  @override
  final String phoneNumber;

  factory _$PhoneVerificationRequest(
          [void Function(PhoneVerificationRequestBuilder)? updates]) =>
      (PhoneVerificationRequestBuilder()..update(updates))._build();

  _$PhoneVerificationRequest._({required this.phoneNumber}) : super._();
  @override
  PhoneVerificationRequest rebuild(
          void Function(PhoneVerificationRequestBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  PhoneVerificationRequestBuilder toBuilder() =>
      PhoneVerificationRequestBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is PhoneVerificationRequest &&
        phoneNumber == other.phoneNumber;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, phoneNumber.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'PhoneVerificationRequest')
          ..add('phoneNumber', phoneNumber))
        .toString();
  }
}

class PhoneVerificationRequestBuilder
    implements
        Builder<PhoneVerificationRequest, PhoneVerificationRequestBuilder> {
  _$PhoneVerificationRequest? _$v;

  String? _phoneNumber;
  String? get phoneNumber => _$this._phoneNumber;
  set phoneNumber(String? phoneNumber) => _$this._phoneNumber = phoneNumber;

  PhoneVerificationRequestBuilder() {
    PhoneVerificationRequest._defaults(this);
  }

  PhoneVerificationRequestBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _phoneNumber = $v.phoneNumber;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(PhoneVerificationRequest other) {
    _$v = other as _$PhoneVerificationRequest;
  }

  @override
  void update(void Function(PhoneVerificationRequestBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  PhoneVerificationRequest build() => _build();

  _$PhoneVerificationRequest _build() {
    final _$result = _$v ??
        _$PhoneVerificationRequest._(
          phoneNumber: BuiltValueNullFieldError.checkNotNull(
              phoneNumber, r'PhoneVerificationRequest', 'phoneNumber'),
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
