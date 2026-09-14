// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'phone_verification_response.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$PhoneVerificationResponse extends PhoneVerificationResponse {
  @override
  final String carrierType;
  @override
  final String? countryCode;
  @override
  final bool deliverable;
  @override
  final String? error;
  @override
  final String formattedNumber;
  @override
  final bool valid;

  factory _$PhoneVerificationResponse(
          [void Function(PhoneVerificationResponseBuilder)? updates]) =>
      (PhoneVerificationResponseBuilder()..update(updates))._build();

  _$PhoneVerificationResponse._(
      {required this.carrierType,
      this.countryCode,
      required this.deliverable,
      this.error,
      required this.formattedNumber,
      required this.valid})
      : super._();
  @override
  PhoneVerificationResponse rebuild(
          void Function(PhoneVerificationResponseBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  PhoneVerificationResponseBuilder toBuilder() =>
      PhoneVerificationResponseBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is PhoneVerificationResponse &&
        carrierType == other.carrierType &&
        countryCode == other.countryCode &&
        deliverable == other.deliverable &&
        error == other.error &&
        formattedNumber == other.formattedNumber &&
        valid == other.valid;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, carrierType.hashCode);
    _$hash = $jc(_$hash, countryCode.hashCode);
    _$hash = $jc(_$hash, deliverable.hashCode);
    _$hash = $jc(_$hash, error.hashCode);
    _$hash = $jc(_$hash, formattedNumber.hashCode);
    _$hash = $jc(_$hash, valid.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'PhoneVerificationResponse')
          ..add('carrierType', carrierType)
          ..add('countryCode', countryCode)
          ..add('deliverable', deliverable)
          ..add('error', error)
          ..add('formattedNumber', formattedNumber)
          ..add('valid', valid))
        .toString();
  }
}

class PhoneVerificationResponseBuilder
    implements
        Builder<PhoneVerificationResponse, PhoneVerificationResponseBuilder> {
  _$PhoneVerificationResponse? _$v;

  String? _carrierType;
  String? get carrierType => _$this._carrierType;
  set carrierType(String? carrierType) => _$this._carrierType = carrierType;

  String? _countryCode;
  String? get countryCode => _$this._countryCode;
  set countryCode(String? countryCode) => _$this._countryCode = countryCode;

  bool? _deliverable;
  bool? get deliverable => _$this._deliverable;
  set deliverable(bool? deliverable) => _$this._deliverable = deliverable;

  String? _error;
  String? get error => _$this._error;
  set error(String? error) => _$this._error = error;

  String? _formattedNumber;
  String? get formattedNumber => _$this._formattedNumber;
  set formattedNumber(String? formattedNumber) =>
      _$this._formattedNumber = formattedNumber;

  bool? _valid;
  bool? get valid => _$this._valid;
  set valid(bool? valid) => _$this._valid = valid;

  PhoneVerificationResponseBuilder() {
    PhoneVerificationResponse._defaults(this);
  }

  PhoneVerificationResponseBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _carrierType = $v.carrierType;
      _countryCode = $v.countryCode;
      _deliverable = $v.deliverable;
      _error = $v.error;
      _formattedNumber = $v.formattedNumber;
      _valid = $v.valid;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(PhoneVerificationResponse other) {
    _$v = other as _$PhoneVerificationResponse;
  }

  @override
  void update(void Function(PhoneVerificationResponseBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  PhoneVerificationResponse build() => _build();

  _$PhoneVerificationResponse _build() {
    final _$result = _$v ??
        _$PhoneVerificationResponse._(
          carrierType: BuiltValueNullFieldError.checkNotNull(
              carrierType, r'PhoneVerificationResponse', 'carrierType'),
          countryCode: countryCode,
          deliverable: BuiltValueNullFieldError.checkNotNull(
              deliverable, r'PhoneVerificationResponse', 'deliverable'),
          error: error,
          formattedNumber: BuiltValueNullFieldError.checkNotNull(
              formattedNumber, r'PhoneVerificationResponse', 'formattedNumber'),
          valid: BuiltValueNullFieldError.checkNotNull(
              valid, r'PhoneVerificationResponse', 'valid'),
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
