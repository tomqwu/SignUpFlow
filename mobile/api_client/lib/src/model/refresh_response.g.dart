// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'refresh_response.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$RefreshResponse extends RefreshResponse {
  @override
  final String refreshToken;
  @override
  final String token;

  factory _$RefreshResponse([void Function(RefreshResponseBuilder)? updates]) =>
      (RefreshResponseBuilder()..update(updates))._build();

  _$RefreshResponse._({required this.refreshToken, required this.token})
      : super._();
  @override
  RefreshResponse rebuild(void Function(RefreshResponseBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  RefreshResponseBuilder toBuilder() => RefreshResponseBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is RefreshResponse &&
        refreshToken == other.refreshToken &&
        token == other.token;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, refreshToken.hashCode);
    _$hash = $jc(_$hash, token.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'RefreshResponse')
          ..add('refreshToken', refreshToken)
          ..add('token', token))
        .toString();
  }
}

class RefreshResponseBuilder
    implements Builder<RefreshResponse, RefreshResponseBuilder> {
  _$RefreshResponse? _$v;

  String? _refreshToken;
  String? get refreshToken => _$this._refreshToken;
  set refreshToken(String? refreshToken) => _$this._refreshToken = refreshToken;

  String? _token;
  String? get token => _$this._token;
  set token(String? token) => _$this._token = token;

  RefreshResponseBuilder() {
    RefreshResponse._defaults(this);
  }

  RefreshResponseBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _refreshToken = $v.refreshToken;
      _token = $v.token;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(RefreshResponse other) {
    _$v = other as _$RefreshResponse;
  }

  @override
  void update(void Function(RefreshResponseBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  RefreshResponse build() => _build();

  _$RefreshResponse _build() {
    final _$result = _$v ??
        _$RefreshResponse._(
          refreshToken: BuiltValueNullFieldError.checkNotNull(
              refreshToken, r'RefreshResponse', 'refreshToken'),
          token: BuiltValueNullFieldError.checkNotNull(
              token, r'RefreshResponse', 'token'),
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
