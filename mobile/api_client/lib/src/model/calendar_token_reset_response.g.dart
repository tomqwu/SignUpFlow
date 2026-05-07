// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'calendar_token_reset_response.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$CalendarTokenResetResponse extends CalendarTokenResetResponse {
  @override
  final String httpsUrl;
  @override
  final String message;
  @override
  final String token;
  @override
  final String webcalUrl;

  factory _$CalendarTokenResetResponse(
          [void Function(CalendarTokenResetResponseBuilder)? updates]) =>
      (CalendarTokenResetResponseBuilder()..update(updates))._build();

  _$CalendarTokenResetResponse._(
      {required this.httpsUrl,
      required this.message,
      required this.token,
      required this.webcalUrl})
      : super._();
  @override
  CalendarTokenResetResponse rebuild(
          void Function(CalendarTokenResetResponseBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  CalendarTokenResetResponseBuilder toBuilder() =>
      CalendarTokenResetResponseBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is CalendarTokenResetResponse &&
        httpsUrl == other.httpsUrl &&
        message == other.message &&
        token == other.token &&
        webcalUrl == other.webcalUrl;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, httpsUrl.hashCode);
    _$hash = $jc(_$hash, message.hashCode);
    _$hash = $jc(_$hash, token.hashCode);
    _$hash = $jc(_$hash, webcalUrl.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'CalendarTokenResetResponse')
          ..add('httpsUrl', httpsUrl)
          ..add('message', message)
          ..add('token', token)
          ..add('webcalUrl', webcalUrl))
        .toString();
  }
}

class CalendarTokenResetResponseBuilder
    implements
        Builder<CalendarTokenResetResponse, CalendarTokenResetResponseBuilder> {
  _$CalendarTokenResetResponse? _$v;

  String? _httpsUrl;
  String? get httpsUrl => _$this._httpsUrl;
  set httpsUrl(String? httpsUrl) => _$this._httpsUrl = httpsUrl;

  String? _message;
  String? get message => _$this._message;
  set message(String? message) => _$this._message = message;

  String? _token;
  String? get token => _$this._token;
  set token(String? token) => _$this._token = token;

  String? _webcalUrl;
  String? get webcalUrl => _$this._webcalUrl;
  set webcalUrl(String? webcalUrl) => _$this._webcalUrl = webcalUrl;

  CalendarTokenResetResponseBuilder() {
    CalendarTokenResetResponse._defaults(this);
  }

  CalendarTokenResetResponseBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _httpsUrl = $v.httpsUrl;
      _message = $v.message;
      _token = $v.token;
      _webcalUrl = $v.webcalUrl;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(CalendarTokenResetResponse other) {
    _$v = other as _$CalendarTokenResetResponse;
  }

  @override
  void update(void Function(CalendarTokenResetResponseBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  CalendarTokenResetResponse build() => _build();

  _$CalendarTokenResetResponse _build() {
    final _$result = _$v ??
        _$CalendarTokenResetResponse._(
          httpsUrl: BuiltValueNullFieldError.checkNotNull(
              httpsUrl, r'CalendarTokenResetResponse', 'httpsUrl'),
          message: BuiltValueNullFieldError.checkNotNull(
              message, r'CalendarTokenResetResponse', 'message'),
          token: BuiltValueNullFieldError.checkNotNull(
              token, r'CalendarTokenResetResponse', 'token'),
          webcalUrl: BuiltValueNullFieldError.checkNotNull(
              webcalUrl, r'CalendarTokenResetResponse', 'webcalUrl'),
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
