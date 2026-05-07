// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'fairness_stats.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$FairnessStats extends FairnessStats {
  @override
  final BuiltMap<String, int> histogram;
  @override
  final BuiltMap<String, int> perPersonCounts;
  @override
  final num stdev;

  factory _$FairnessStats([void Function(FairnessStatsBuilder)? updates]) =>
      (FairnessStatsBuilder()..update(updates))._build();

  _$FairnessStats._(
      {required this.histogram,
      required this.perPersonCounts,
      required this.stdev})
      : super._();
  @override
  FairnessStats rebuild(void Function(FairnessStatsBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  FairnessStatsBuilder toBuilder() => FairnessStatsBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is FairnessStats &&
        histogram == other.histogram &&
        perPersonCounts == other.perPersonCounts &&
        stdev == other.stdev;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, histogram.hashCode);
    _$hash = $jc(_$hash, perPersonCounts.hashCode);
    _$hash = $jc(_$hash, stdev.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'FairnessStats')
          ..add('histogram', histogram)
          ..add('perPersonCounts', perPersonCounts)
          ..add('stdev', stdev))
        .toString();
  }
}

class FairnessStatsBuilder
    implements Builder<FairnessStats, FairnessStatsBuilder> {
  _$FairnessStats? _$v;

  MapBuilder<String, int>? _histogram;
  MapBuilder<String, int> get histogram =>
      _$this._histogram ??= MapBuilder<String, int>();
  set histogram(MapBuilder<String, int>? histogram) =>
      _$this._histogram = histogram;

  MapBuilder<String, int>? _perPersonCounts;
  MapBuilder<String, int> get perPersonCounts =>
      _$this._perPersonCounts ??= MapBuilder<String, int>();
  set perPersonCounts(MapBuilder<String, int>? perPersonCounts) =>
      _$this._perPersonCounts = perPersonCounts;

  num? _stdev;
  num? get stdev => _$this._stdev;
  set stdev(num? stdev) => _$this._stdev = stdev;

  FairnessStatsBuilder() {
    FairnessStats._defaults(this);
  }

  FairnessStatsBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _histogram = $v.histogram.toBuilder();
      _perPersonCounts = $v.perPersonCounts.toBuilder();
      _stdev = $v.stdev;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(FairnessStats other) {
    _$v = other as _$FairnessStats;
  }

  @override
  void update(void Function(FairnessStatsBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  FairnessStats build() => _build();

  _$FairnessStats _build() {
    _$FairnessStats _$result;
    try {
      _$result = _$v ??
          _$FairnessStats._(
            histogram: histogram.build(),
            perPersonCounts: perPersonCounts.build(),
            stdev: BuiltValueNullFieldError.checkNotNull(
                stdev, r'FairnessStats', 'stdev'),
          );
    } catch (_) {
      late String _$failedField;
      try {
        _$failedField = 'histogram';
        histogram.build();
        _$failedField = 'perPersonCounts';
        perPersonCounts.build();
      } catch (e) {
        throw BuiltValueNestedFieldError(
            r'FairnessStats', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
