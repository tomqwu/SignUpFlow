// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'solution_metrics.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$SolutionMetrics extends SolutionMetrics {
  @override
  final FairnessMetrics fairness;
  @override
  final int hardViolations;
  @override
  final num healthScore;
  @override
  final num softScore;
  @override
  final num solveMs;
  @override
  final StabilityMetrics? stability;

  factory _$SolutionMetrics([void Function(SolutionMetricsBuilder)? updates]) =>
      (SolutionMetricsBuilder()..update(updates))._build();

  _$SolutionMetrics._(
      {required this.fairness,
      required this.hardViolations,
      required this.healthScore,
      required this.softScore,
      required this.solveMs,
      this.stability})
      : super._();
  @override
  SolutionMetrics rebuild(void Function(SolutionMetricsBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  SolutionMetricsBuilder toBuilder() => SolutionMetricsBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is SolutionMetrics &&
        fairness == other.fairness &&
        hardViolations == other.hardViolations &&
        healthScore == other.healthScore &&
        softScore == other.softScore &&
        solveMs == other.solveMs &&
        stability == other.stability;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, fairness.hashCode);
    _$hash = $jc(_$hash, hardViolations.hashCode);
    _$hash = $jc(_$hash, healthScore.hashCode);
    _$hash = $jc(_$hash, softScore.hashCode);
    _$hash = $jc(_$hash, solveMs.hashCode);
    _$hash = $jc(_$hash, stability.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'SolutionMetrics')
          ..add('fairness', fairness)
          ..add('hardViolations', hardViolations)
          ..add('healthScore', healthScore)
          ..add('softScore', softScore)
          ..add('solveMs', solveMs)
          ..add('stability', stability))
        .toString();
  }
}

class SolutionMetricsBuilder
    implements Builder<SolutionMetrics, SolutionMetricsBuilder> {
  _$SolutionMetrics? _$v;

  FairnessMetricsBuilder? _fairness;
  FairnessMetricsBuilder get fairness =>
      _$this._fairness ??= FairnessMetricsBuilder();
  set fairness(FairnessMetricsBuilder? fairness) => _$this._fairness = fairness;

  int? _hardViolations;
  int? get hardViolations => _$this._hardViolations;
  set hardViolations(int? hardViolations) =>
      _$this._hardViolations = hardViolations;

  num? _healthScore;
  num? get healthScore => _$this._healthScore;
  set healthScore(num? healthScore) => _$this._healthScore = healthScore;

  num? _softScore;
  num? get softScore => _$this._softScore;
  set softScore(num? softScore) => _$this._softScore = softScore;

  num? _solveMs;
  num? get solveMs => _$this._solveMs;
  set solveMs(num? solveMs) => _$this._solveMs = solveMs;

  StabilityMetricsBuilder? _stability;
  StabilityMetricsBuilder get stability =>
      _$this._stability ??= StabilityMetricsBuilder();
  set stability(StabilityMetricsBuilder? stability) =>
      _$this._stability = stability;

  SolutionMetricsBuilder() {
    SolutionMetrics._defaults(this);
  }

  SolutionMetricsBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _fairness = $v.fairness.toBuilder();
      _hardViolations = $v.hardViolations;
      _healthScore = $v.healthScore;
      _softScore = $v.softScore;
      _solveMs = $v.solveMs;
      _stability = $v.stability?.toBuilder();
      _$v = null;
    }
    return this;
  }

  @override
  void replace(SolutionMetrics other) {
    _$v = other as _$SolutionMetrics;
  }

  @override
  void update(void Function(SolutionMetricsBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  SolutionMetrics build() => _build();

  _$SolutionMetrics _build() {
    _$SolutionMetrics _$result;
    try {
      _$result = _$v ??
          _$SolutionMetrics._(
            fairness: fairness.build(),
            hardViolations: BuiltValueNullFieldError.checkNotNull(
                hardViolations, r'SolutionMetrics', 'hardViolations'),
            healthScore: BuiltValueNullFieldError.checkNotNull(
                healthScore, r'SolutionMetrics', 'healthScore'),
            softScore: BuiltValueNullFieldError.checkNotNull(
                softScore, r'SolutionMetrics', 'softScore'),
            solveMs: BuiltValueNullFieldError.checkNotNull(
                solveMs, r'SolutionMetrics', 'solveMs'),
            stability: _stability?.build(),
          );
    } catch (_) {
      late String _$failedField;
      try {
        _$failedField = 'fairness';
        fairness.build();

        _$failedField = 'stability';
        _stability?.build();
      } catch (e) {
        throw BuiltValueNestedFieldError(
            r'SolutionMetrics', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
