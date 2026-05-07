// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'notification_stats_response.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$NotificationStatsResponse extends NotificationStatsResponse {
  @override
  final int daysAnalyzed;
  @override
  final int deliveredNotifications;
  @override
  final String orgId;
  @override
  final BuiltList<NotificationResponse> recentFailures;
  @override
  final BuiltMap<String, int> statusBreakdown;
  @override
  final num successRate;
  @override
  final int totalNotifications;
  @override
  final BuiltMap<String, int> typeBreakdown;

  factory _$NotificationStatsResponse(
          [void Function(NotificationStatsResponseBuilder)? updates]) =>
      (NotificationStatsResponseBuilder()..update(updates))._build();

  _$NotificationStatsResponse._(
      {required this.daysAnalyzed,
      required this.deliveredNotifications,
      required this.orgId,
      required this.recentFailures,
      required this.statusBreakdown,
      required this.successRate,
      required this.totalNotifications,
      required this.typeBreakdown})
      : super._();
  @override
  NotificationStatsResponse rebuild(
          void Function(NotificationStatsResponseBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  NotificationStatsResponseBuilder toBuilder() =>
      NotificationStatsResponseBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is NotificationStatsResponse &&
        daysAnalyzed == other.daysAnalyzed &&
        deliveredNotifications == other.deliveredNotifications &&
        orgId == other.orgId &&
        recentFailures == other.recentFailures &&
        statusBreakdown == other.statusBreakdown &&
        successRate == other.successRate &&
        totalNotifications == other.totalNotifications &&
        typeBreakdown == other.typeBreakdown;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, daysAnalyzed.hashCode);
    _$hash = $jc(_$hash, deliveredNotifications.hashCode);
    _$hash = $jc(_$hash, orgId.hashCode);
    _$hash = $jc(_$hash, recentFailures.hashCode);
    _$hash = $jc(_$hash, statusBreakdown.hashCode);
    _$hash = $jc(_$hash, successRate.hashCode);
    _$hash = $jc(_$hash, totalNotifications.hashCode);
    _$hash = $jc(_$hash, typeBreakdown.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'NotificationStatsResponse')
          ..add('daysAnalyzed', daysAnalyzed)
          ..add('deliveredNotifications', deliveredNotifications)
          ..add('orgId', orgId)
          ..add('recentFailures', recentFailures)
          ..add('statusBreakdown', statusBreakdown)
          ..add('successRate', successRate)
          ..add('totalNotifications', totalNotifications)
          ..add('typeBreakdown', typeBreakdown))
        .toString();
  }
}

class NotificationStatsResponseBuilder
    implements
        Builder<NotificationStatsResponse, NotificationStatsResponseBuilder> {
  _$NotificationStatsResponse? _$v;

  int? _daysAnalyzed;
  int? get daysAnalyzed => _$this._daysAnalyzed;
  set daysAnalyzed(int? daysAnalyzed) => _$this._daysAnalyzed = daysAnalyzed;

  int? _deliveredNotifications;
  int? get deliveredNotifications => _$this._deliveredNotifications;
  set deliveredNotifications(int? deliveredNotifications) =>
      _$this._deliveredNotifications = deliveredNotifications;

  String? _orgId;
  String? get orgId => _$this._orgId;
  set orgId(String? orgId) => _$this._orgId = orgId;

  ListBuilder<NotificationResponse>? _recentFailures;
  ListBuilder<NotificationResponse> get recentFailures =>
      _$this._recentFailures ??= ListBuilder<NotificationResponse>();
  set recentFailures(ListBuilder<NotificationResponse>? recentFailures) =>
      _$this._recentFailures = recentFailures;

  MapBuilder<String, int>? _statusBreakdown;
  MapBuilder<String, int> get statusBreakdown =>
      _$this._statusBreakdown ??= MapBuilder<String, int>();
  set statusBreakdown(MapBuilder<String, int>? statusBreakdown) =>
      _$this._statusBreakdown = statusBreakdown;

  num? _successRate;
  num? get successRate => _$this._successRate;
  set successRate(num? successRate) => _$this._successRate = successRate;

  int? _totalNotifications;
  int? get totalNotifications => _$this._totalNotifications;
  set totalNotifications(int? totalNotifications) =>
      _$this._totalNotifications = totalNotifications;

  MapBuilder<String, int>? _typeBreakdown;
  MapBuilder<String, int> get typeBreakdown =>
      _$this._typeBreakdown ??= MapBuilder<String, int>();
  set typeBreakdown(MapBuilder<String, int>? typeBreakdown) =>
      _$this._typeBreakdown = typeBreakdown;

  NotificationStatsResponseBuilder() {
    NotificationStatsResponse._defaults(this);
  }

  NotificationStatsResponseBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _daysAnalyzed = $v.daysAnalyzed;
      _deliveredNotifications = $v.deliveredNotifications;
      _orgId = $v.orgId;
      _recentFailures = $v.recentFailures.toBuilder();
      _statusBreakdown = $v.statusBreakdown.toBuilder();
      _successRate = $v.successRate;
      _totalNotifications = $v.totalNotifications;
      _typeBreakdown = $v.typeBreakdown.toBuilder();
      _$v = null;
    }
    return this;
  }

  @override
  void replace(NotificationStatsResponse other) {
    _$v = other as _$NotificationStatsResponse;
  }

  @override
  void update(void Function(NotificationStatsResponseBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  NotificationStatsResponse build() => _build();

  _$NotificationStatsResponse _build() {
    _$NotificationStatsResponse _$result;
    try {
      _$result = _$v ??
          _$NotificationStatsResponse._(
            daysAnalyzed: BuiltValueNullFieldError.checkNotNull(
                daysAnalyzed, r'NotificationStatsResponse', 'daysAnalyzed'),
            deliveredNotifications: BuiltValueNullFieldError.checkNotNull(
                deliveredNotifications,
                r'NotificationStatsResponse',
                'deliveredNotifications'),
            orgId: BuiltValueNullFieldError.checkNotNull(
                orgId, r'NotificationStatsResponse', 'orgId'),
            recentFailures: recentFailures.build(),
            statusBreakdown: statusBreakdown.build(),
            successRate: BuiltValueNullFieldError.checkNotNull(
                successRate, r'NotificationStatsResponse', 'successRate'),
            totalNotifications: BuiltValueNullFieldError.checkNotNull(
                totalNotifications,
                r'NotificationStatsResponse',
                'totalNotifications'),
            typeBreakdown: typeBreakdown.build(),
          );
    } catch (_) {
      late String _$failedField;
      try {
        _$failedField = 'recentFailures';
        recentFailures.build();
        _$failedField = 'statusBreakdown';
        statusBreakdown.build();

        _$failedField = 'typeBreakdown';
        typeBreakdown.build();
      } catch (e) {
        throw BuiltValueNestedFieldError(
            r'NotificationStatsResponse', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
