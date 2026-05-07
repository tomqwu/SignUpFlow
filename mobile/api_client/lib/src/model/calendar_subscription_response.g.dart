// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'calendar_subscription_response.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$CalendarSubscriptionResponse extends CalendarSubscriptionResponse {
  @override
  final String httpsUrl;
  @override
  final String message;
  @override
  final String token;
  @override
  final String webcalUrl;

  factory _$CalendarSubscriptionResponse(
          [void Function(CalendarSubscriptionResponseBuilder)? updates]) =>
      (CalendarSubscriptionResponseBuilder()..update(updates))._build();

  _$CalendarSubscriptionResponse._(
      {required this.httpsUrl,
      required this.message,
      required this.token,
      required this.webcalUrl})
      : super._();
  @override
  CalendarSubscriptionResponse rebuild(
          void Function(CalendarSubscriptionResponseBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  CalendarSubscriptionResponseBuilder toBuilder() =>
      CalendarSubscriptionResponseBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is CalendarSubscriptionResponse &&
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
    return (newBuiltValueToStringHelper(r'CalendarSubscriptionResponse')
          ..add('httpsUrl', httpsUrl)
          ..add('message', message)
          ..add('token', token)
          ..add('webcalUrl', webcalUrl))
        .toString();
  }
}

class CalendarSubscriptionResponseBuilder
    implements
        Builder<CalendarSubscriptionResponse,
            CalendarSubscriptionResponseBuilder> {
  _$CalendarSubscriptionResponse? _$v;

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

  CalendarSubscriptionResponseBuilder() {
    CalendarSubscriptionResponse._defaults(this);
  }

  CalendarSubscriptionResponseBuilder get _$this {
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
  void replace(CalendarSubscriptionResponse other) {
    _$v = other as _$CalendarSubscriptionResponse;
  }

  @override
  void update(void Function(CalendarSubscriptionResponseBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  CalendarSubscriptionResponse build() => _build();

  _$CalendarSubscriptionResponse _build() {
    final _$result = _$v ??
        _$CalendarSubscriptionResponse._(
          httpsUrl: BuiltValueNullFieldError.checkNotNull(
              httpsUrl, r'CalendarSubscriptionResponse', 'httpsUrl'),
          message: BuiltValueNullFieldError.checkNotNull(
              message, r'CalendarSubscriptionResponse', 'message'),
          token: BuiltValueNullFieldError.checkNotNull(
              token, r'CalendarSubscriptionResponse', 'token'),
          webcalUrl: BuiltValueNullFieldError.checkNotNull(
              webcalUrl, r'CalendarSubscriptionResponse', 'webcalUrl'),
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
