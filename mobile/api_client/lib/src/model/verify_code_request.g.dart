// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'verify_code_request.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$VerifyCodeRequest extends VerifyCodeRequest {
  @override
  final int code;
  @override
  final String personId;

  factory _$VerifyCodeRequest(
          [void Function(VerifyCodeRequestBuilder)? updates]) =>
      (VerifyCodeRequestBuilder()..update(updates))._build();

  _$VerifyCodeRequest._({required this.code, required this.personId})
      : super._();
  @override
  VerifyCodeRequest rebuild(void Function(VerifyCodeRequestBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  VerifyCodeRequestBuilder toBuilder() =>
      VerifyCodeRequestBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is VerifyCodeRequest &&
        code == other.code &&
        personId == other.personId;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, code.hashCode);
    _$hash = $jc(_$hash, personId.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'VerifyCodeRequest')
          ..add('code', code)
          ..add('personId', personId))
        .toString();
  }
}

class VerifyCodeRequestBuilder
    implements Builder<VerifyCodeRequest, VerifyCodeRequestBuilder> {
  _$VerifyCodeRequest? _$v;

  int? _code;
  int? get code => _$this._code;
  set code(int? code) => _$this._code = code;

  String? _personId;
  String? get personId => _$this._personId;
  set personId(String? personId) => _$this._personId = personId;

  VerifyCodeRequestBuilder() {
    VerifyCodeRequest._defaults(this);
  }

  VerifyCodeRequestBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _code = $v.code;
      _personId = $v.personId;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(VerifyCodeRequest other) {
    _$v = other as _$VerifyCodeRequest;
  }

  @override
  void update(void Function(VerifyCodeRequestBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  VerifyCodeRequest build() => _build();

  _$VerifyCodeRequest _build() {
    final _$result = _$v ??
        _$VerifyCodeRequest._(
          code: BuiltValueNullFieldError.checkNotNull(
              code, r'VerifyCodeRequest', 'code'),
          personId: BuiltValueNullFieldError.checkNotNull(
              personId, r'VerifyCodeRequest', 'personId'),
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
