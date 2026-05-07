// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'stability_metrics.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$StabilityMetrics extends StabilityMetrics {
  @override
  final int? affectedPersons;
  @override
  final int? movesFromPublished;

  factory _$StabilityMetrics(
          [void Function(StabilityMetricsBuilder)? updates]) =>
      (StabilityMetricsBuilder()..update(updates))._build();

  _$StabilityMetrics._({this.affectedPersons, this.movesFromPublished})
      : super._();
  @override
  StabilityMetrics rebuild(void Function(StabilityMetricsBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  StabilityMetricsBuilder toBuilder() =>
      StabilityMetricsBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is StabilityMetrics &&
        affectedPersons == other.affectedPersons &&
        movesFromPublished == other.movesFromPublished;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, affectedPersons.hashCode);
    _$hash = $jc(_$hash, movesFromPublished.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'StabilityMetrics')
          ..add('affectedPersons', affectedPersons)
          ..add('movesFromPublished', movesFromPublished))
        .toString();
  }
}

class StabilityMetricsBuilder
    implements Builder<StabilityMetrics, StabilityMetricsBuilder> {
  _$StabilityMetrics? _$v;

  int? _affectedPersons;
  int? get affectedPersons => _$this._affectedPersons;
  set affectedPersons(int? affectedPersons) =>
      _$this._affectedPersons = affectedPersons;

  int? _movesFromPublished;
  int? get movesFromPublished => _$this._movesFromPublished;
  set movesFromPublished(int? movesFromPublished) =>
      _$this._movesFromPublished = movesFromPublished;

  StabilityMetricsBuilder() {
    StabilityMetrics._defaults(this);
  }

  StabilityMetricsBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _affectedPersons = $v.affectedPersons;
      _movesFromPublished = $v.movesFromPublished;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(StabilityMetrics other) {
    _$v = other as _$StabilityMetrics;
  }

  @override
  void update(void Function(StabilityMetricsBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  StabilityMetrics build() => _build();

  _$StabilityMetrics _build() {
    final _$result = _$v ??
        _$StabilityMetrics._(
          affectedPersons: affectedPersons,
          movesFromPublished: movesFromPublished,
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
