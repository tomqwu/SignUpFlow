// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'sms_usage_stats_response.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$SmsUsageStatsResponse extends SmsUsageStatsResponse {
  @override
  final int budgetLimitCents;
  @override
  final num budgetUsedPercentage;
  @override
  final int messagesDelivered;
  @override
  final int messagesFailed;
  @override
  final int? messagesRemaining;
  @override
  final int messagesSent;
  @override
  final String monthYear;
  @override
  final int totalCostCents;

  factory _$SmsUsageStatsResponse(
          [void Function(SmsUsageStatsResponseBuilder)? updates]) =>
      (SmsUsageStatsResponseBuilder()..update(updates))._build();

  _$SmsUsageStatsResponse._(
      {required this.budgetLimitCents,
      required this.budgetUsedPercentage,
      required this.messagesDelivered,
      required this.messagesFailed,
      this.messagesRemaining,
      required this.messagesSent,
      required this.monthYear,
      required this.totalCostCents})
      : super._();
  @override
  SmsUsageStatsResponse rebuild(
          void Function(SmsUsageStatsResponseBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  SmsUsageStatsResponseBuilder toBuilder() =>
      SmsUsageStatsResponseBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is SmsUsageStatsResponse &&
        budgetLimitCents == other.budgetLimitCents &&
        budgetUsedPercentage == other.budgetUsedPercentage &&
        messagesDelivered == other.messagesDelivered &&
        messagesFailed == other.messagesFailed &&
        messagesRemaining == other.messagesRemaining &&
        messagesSent == other.messagesSent &&
        monthYear == other.monthYear &&
        totalCostCents == other.totalCostCents;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, budgetLimitCents.hashCode);
    _$hash = $jc(_$hash, budgetUsedPercentage.hashCode);
    _$hash = $jc(_$hash, messagesDelivered.hashCode);
    _$hash = $jc(_$hash, messagesFailed.hashCode);
    _$hash = $jc(_$hash, messagesRemaining.hashCode);
    _$hash = $jc(_$hash, messagesSent.hashCode);
    _$hash = $jc(_$hash, monthYear.hashCode);
    _$hash = $jc(_$hash, totalCostCents.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'SmsUsageStatsResponse')
          ..add('budgetLimitCents', budgetLimitCents)
          ..add('budgetUsedPercentage', budgetUsedPercentage)
          ..add('messagesDelivered', messagesDelivered)
          ..add('messagesFailed', messagesFailed)
          ..add('messagesRemaining', messagesRemaining)
          ..add('messagesSent', messagesSent)
          ..add('monthYear', monthYear)
          ..add('totalCostCents', totalCostCents))
        .toString();
  }
}

class SmsUsageStatsResponseBuilder
    implements Builder<SmsUsageStatsResponse, SmsUsageStatsResponseBuilder> {
  _$SmsUsageStatsResponse? _$v;

  int? _budgetLimitCents;
  int? get budgetLimitCents => _$this._budgetLimitCents;
  set budgetLimitCents(int? budgetLimitCents) =>
      _$this._budgetLimitCents = budgetLimitCents;

  num? _budgetUsedPercentage;
  num? get budgetUsedPercentage => _$this._budgetUsedPercentage;
  set budgetUsedPercentage(num? budgetUsedPercentage) =>
      _$this._budgetUsedPercentage = budgetUsedPercentage;

  int? _messagesDelivered;
  int? get messagesDelivered => _$this._messagesDelivered;
  set messagesDelivered(int? messagesDelivered) =>
      _$this._messagesDelivered = messagesDelivered;

  int? _messagesFailed;
  int? get messagesFailed => _$this._messagesFailed;
  set messagesFailed(int? messagesFailed) =>
      _$this._messagesFailed = messagesFailed;

  int? _messagesRemaining;
  int? get messagesRemaining => _$this._messagesRemaining;
  set messagesRemaining(int? messagesRemaining) =>
      _$this._messagesRemaining = messagesRemaining;

  int? _messagesSent;
  int? get messagesSent => _$this._messagesSent;
  set messagesSent(int? messagesSent) => _$this._messagesSent = messagesSent;

  String? _monthYear;
  String? get monthYear => _$this._monthYear;
  set monthYear(String? monthYear) => _$this._monthYear = monthYear;

  int? _totalCostCents;
  int? get totalCostCents => _$this._totalCostCents;
  set totalCostCents(int? totalCostCents) =>
      _$this._totalCostCents = totalCostCents;

  SmsUsageStatsResponseBuilder() {
    SmsUsageStatsResponse._defaults(this);
  }

  SmsUsageStatsResponseBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _budgetLimitCents = $v.budgetLimitCents;
      _budgetUsedPercentage = $v.budgetUsedPercentage;
      _messagesDelivered = $v.messagesDelivered;
      _messagesFailed = $v.messagesFailed;
      _messagesRemaining = $v.messagesRemaining;
      _messagesSent = $v.messagesSent;
      _monthYear = $v.monthYear;
      _totalCostCents = $v.totalCostCents;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(SmsUsageStatsResponse other) {
    _$v = other as _$SmsUsageStatsResponse;
  }

  @override
  void update(void Function(SmsUsageStatsResponseBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  SmsUsageStatsResponse build() => _build();

  _$SmsUsageStatsResponse _build() {
    final _$result = _$v ??
        _$SmsUsageStatsResponse._(
          budgetLimitCents: BuiltValueNullFieldError.checkNotNull(
              budgetLimitCents, r'SmsUsageStatsResponse', 'budgetLimitCents'),
          budgetUsedPercentage: BuiltValueNullFieldError.checkNotNull(
              budgetUsedPercentage,
              r'SmsUsageStatsResponse',
              'budgetUsedPercentage'),
          messagesDelivered: BuiltValueNullFieldError.checkNotNull(
              messagesDelivered, r'SmsUsageStatsResponse', 'messagesDelivered'),
          messagesFailed: BuiltValueNullFieldError.checkNotNull(
              messagesFailed, r'SmsUsageStatsResponse', 'messagesFailed'),
          messagesRemaining: messagesRemaining,
          messagesSent: BuiltValueNullFieldError.checkNotNull(
              messagesSent, r'SmsUsageStatsResponse', 'messagesSent'),
          monthYear: BuiltValueNullFieldError.checkNotNull(
              monthYear, r'SmsUsageStatsResponse', 'monthYear'),
          totalCostCents: BuiltValueNullFieldError.checkNotNull(
              totalCostCents, r'SmsUsageStatsResponse', 'totalCostCents'),
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
