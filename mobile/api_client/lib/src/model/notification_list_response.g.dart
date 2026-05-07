// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'notification_list_response.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$NotificationListResponse extends NotificationListResponse {
  @override
  final int limit;
  @override
  final BuiltList<NotificationResponse> notifications;
  @override
  final int offset;
  @override
  final int total;

  factory _$NotificationListResponse(
          [void Function(NotificationListResponseBuilder)? updates]) =>
      (NotificationListResponseBuilder()..update(updates))._build();

  _$NotificationListResponse._(
      {required this.limit,
      required this.notifications,
      required this.offset,
      required this.total})
      : super._();
  @override
  NotificationListResponse rebuild(
          void Function(NotificationListResponseBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  NotificationListResponseBuilder toBuilder() =>
      NotificationListResponseBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is NotificationListResponse &&
        limit == other.limit &&
        notifications == other.notifications &&
        offset == other.offset &&
        total == other.total;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, limit.hashCode);
    _$hash = $jc(_$hash, notifications.hashCode);
    _$hash = $jc(_$hash, offset.hashCode);
    _$hash = $jc(_$hash, total.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'NotificationListResponse')
          ..add('limit', limit)
          ..add('notifications', notifications)
          ..add('offset', offset)
          ..add('total', total))
        .toString();
  }
}

class NotificationListResponseBuilder
    implements
        Builder<NotificationListResponse, NotificationListResponseBuilder> {
  _$NotificationListResponse? _$v;

  int? _limit;
  int? get limit => _$this._limit;
  set limit(int? limit) => _$this._limit = limit;

  ListBuilder<NotificationResponse>? _notifications;
  ListBuilder<NotificationResponse> get notifications =>
      _$this._notifications ??= ListBuilder<NotificationResponse>();
  set notifications(ListBuilder<NotificationResponse>? notifications) =>
      _$this._notifications = notifications;

  int? _offset;
  int? get offset => _$this._offset;
  set offset(int? offset) => _$this._offset = offset;

  int? _total;
  int? get total => _$this._total;
  set total(int? total) => _$this._total = total;

  NotificationListResponseBuilder() {
    NotificationListResponse._defaults(this);
  }

  NotificationListResponseBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _limit = $v.limit;
      _notifications = $v.notifications.toBuilder();
      _offset = $v.offset;
      _total = $v.total;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(NotificationListResponse other) {
    _$v = other as _$NotificationListResponse;
  }

  @override
  void update(void Function(NotificationListResponseBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  NotificationListResponse build() => _build();

  _$NotificationListResponse _build() {
    _$NotificationListResponse _$result;
    try {
      _$result = _$v ??
          _$NotificationListResponse._(
            limit: BuiltValueNullFieldError.checkNotNull(
                limit, r'NotificationListResponse', 'limit'),
            notifications: notifications.build(),
            offset: BuiltValueNullFieldError.checkNotNull(
                offset, r'NotificationListResponse', 'offset'),
            total: BuiltValueNullFieldError.checkNotNull(
                total, r'NotificationListResponse', 'total'),
          );
    } catch (_) {
      late String _$failedField;
      try {
        _$failedField = 'notifications';
        notifications.build();
      } catch (e) {
        throw BuiltValueNestedFieldError(
            r'NotificationListResponse', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
