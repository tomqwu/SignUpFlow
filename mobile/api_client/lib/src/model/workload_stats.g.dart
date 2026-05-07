// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'workload_stats.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$WorkloadStats extends WorkloadStats {
  @override
  final int distinctPersonsAssigned;
  @override
  final int maxEventsPerPerson;
  @override
  final num medianEventsPerPerson;
  @override
  final int minEventsPerPerson;
  @override
  final int totalEventsAssigned;

  factory _$WorkloadStats([void Function(WorkloadStatsBuilder)? updates]) =>
      (WorkloadStatsBuilder()..update(updates))._build();

  _$WorkloadStats._(
      {required this.distinctPersonsAssigned,
      required this.maxEventsPerPerson,
      required this.medianEventsPerPerson,
      required this.minEventsPerPerson,
      required this.totalEventsAssigned})
      : super._();
  @override
  WorkloadStats rebuild(void Function(WorkloadStatsBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  WorkloadStatsBuilder toBuilder() => WorkloadStatsBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is WorkloadStats &&
        distinctPersonsAssigned == other.distinctPersonsAssigned &&
        maxEventsPerPerson == other.maxEventsPerPerson &&
        medianEventsPerPerson == other.medianEventsPerPerson &&
        minEventsPerPerson == other.minEventsPerPerson &&
        totalEventsAssigned == other.totalEventsAssigned;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, distinctPersonsAssigned.hashCode);
    _$hash = $jc(_$hash, maxEventsPerPerson.hashCode);
    _$hash = $jc(_$hash, medianEventsPerPerson.hashCode);
    _$hash = $jc(_$hash, minEventsPerPerson.hashCode);
    _$hash = $jc(_$hash, totalEventsAssigned.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'WorkloadStats')
          ..add('distinctPersonsAssigned', distinctPersonsAssigned)
          ..add('maxEventsPerPerson', maxEventsPerPerson)
          ..add('medianEventsPerPerson', medianEventsPerPerson)
          ..add('minEventsPerPerson', minEventsPerPerson)
          ..add('totalEventsAssigned', totalEventsAssigned))
        .toString();
  }
}

class WorkloadStatsBuilder
    implements Builder<WorkloadStats, WorkloadStatsBuilder> {
  _$WorkloadStats? _$v;

  int? _distinctPersonsAssigned;
  int? get distinctPersonsAssigned => _$this._distinctPersonsAssigned;
  set distinctPersonsAssigned(int? distinctPersonsAssigned) =>
      _$this._distinctPersonsAssigned = distinctPersonsAssigned;

  int? _maxEventsPerPerson;
  int? get maxEventsPerPerson => _$this._maxEventsPerPerson;
  set maxEventsPerPerson(int? maxEventsPerPerson) =>
      _$this._maxEventsPerPerson = maxEventsPerPerson;

  num? _medianEventsPerPerson;
  num? get medianEventsPerPerson => _$this._medianEventsPerPerson;
  set medianEventsPerPerson(num? medianEventsPerPerson) =>
      _$this._medianEventsPerPerson = medianEventsPerPerson;

  int? _minEventsPerPerson;
  int? get minEventsPerPerson => _$this._minEventsPerPerson;
  set minEventsPerPerson(int? minEventsPerPerson) =>
      _$this._minEventsPerPerson = minEventsPerPerson;

  int? _totalEventsAssigned;
  int? get totalEventsAssigned => _$this._totalEventsAssigned;
  set totalEventsAssigned(int? totalEventsAssigned) =>
      _$this._totalEventsAssigned = totalEventsAssigned;

  WorkloadStatsBuilder() {
    WorkloadStats._defaults(this);
  }

  WorkloadStatsBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _distinctPersonsAssigned = $v.distinctPersonsAssigned;
      _maxEventsPerPerson = $v.maxEventsPerPerson;
      _medianEventsPerPerson = $v.medianEventsPerPerson;
      _minEventsPerPerson = $v.minEventsPerPerson;
      _totalEventsAssigned = $v.totalEventsAssigned;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(WorkloadStats other) {
    _$v = other as _$WorkloadStats;
  }

  @override
  void update(void Function(WorkloadStatsBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  WorkloadStats build() => _build();

  _$WorkloadStats _build() {
    final _$result = _$v ??
        _$WorkloadStats._(
          distinctPersonsAssigned: BuiltValueNullFieldError.checkNotNull(
              distinctPersonsAssigned,
              r'WorkloadStats',
              'distinctPersonsAssigned'),
          maxEventsPerPerson: BuiltValueNullFieldError.checkNotNull(
              maxEventsPerPerson, r'WorkloadStats', 'maxEventsPerPerson'),
          medianEventsPerPerson: BuiltValueNullFieldError.checkNotNull(
              medianEventsPerPerson, r'WorkloadStats', 'medianEventsPerPerson'),
          minEventsPerPerson: BuiltValueNullFieldError.checkNotNull(
              minEventsPerPerson, r'WorkloadStats', 'minEventsPerPerson'),
          totalEventsAssigned: BuiltValueNullFieldError.checkNotNull(
              totalEventsAssigned, r'WorkloadStats', 'totalEventsAssigned'),
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
