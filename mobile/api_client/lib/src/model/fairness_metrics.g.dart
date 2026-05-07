// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'fairness_metrics.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$FairnessMetrics extends FairnessMetrics {
  @override
  final BuiltMap<String, int> perPersonCounts;
  @override
  final num stdev;

  factory _$FairnessMetrics([void Function(FairnessMetricsBuilder)? updates]) =>
      (FairnessMetricsBuilder()..update(updates))._build();

  _$FairnessMetrics._({required this.perPersonCounts, required this.stdev})
      : super._();
  @override
  FairnessMetrics rebuild(void Function(FairnessMetricsBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  FairnessMetricsBuilder toBuilder() => FairnessMetricsBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is FairnessMetrics &&
        perPersonCounts == other.perPersonCounts &&
        stdev == other.stdev;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, perPersonCounts.hashCode);
    _$hash = $jc(_$hash, stdev.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'FairnessMetrics')
          ..add('perPersonCounts', perPersonCounts)
          ..add('stdev', stdev))
        .toString();
  }
}

class FairnessMetricsBuilder
    implements Builder<FairnessMetrics, FairnessMetricsBuilder> {
  _$FairnessMetrics? _$v;

  MapBuilder<String, int>? _perPersonCounts;
  MapBuilder<String, int> get perPersonCounts =>
      _$this._perPersonCounts ??= MapBuilder<String, int>();
  set perPersonCounts(MapBuilder<String, int>? perPersonCounts) =>
      _$this._perPersonCounts = perPersonCounts;

  num? _stdev;
  num? get stdev => _$this._stdev;
  set stdev(num? stdev) => _$this._stdev = stdev;

  FairnessMetricsBuilder() {
    FairnessMetrics._defaults(this);
  }

  FairnessMetricsBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _perPersonCounts = $v.perPersonCounts.toBuilder();
      _stdev = $v.stdev;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(FairnessMetrics other) {
    _$v = other as _$FairnessMetrics;
  }

  @override
  void update(void Function(FairnessMetricsBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  FairnessMetrics build() => _build();

  _$FairnessMetrics _build() {
    _$FairnessMetrics _$result;
    try {
      _$result = _$v ??
          _$FairnessMetrics._(
            perPersonCounts: perPersonCounts.build(),
            stdev: BuiltValueNullFieldError.checkNotNull(
                stdev, r'FairnessMetrics', 'stdev'),
          );
    } catch (_) {
      late String _$failedField;
      try {
        _$failedField = 'perPersonCounts';
        perPersonCounts.build();
      } catch (e) {
        throw BuiltValueNestedFieldError(
            r'FairnessMetrics', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
