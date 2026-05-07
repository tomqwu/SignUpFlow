// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'solution_stats_response.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$SolutionStatsResponse extends SolutionStatsResponse {
  @override
  final FairnessStats fairness;
  @override
  final int solutionId;
  @override
  final StabilityMetrics stability;
  @override
  final WorkloadStats workload;

  factory _$SolutionStatsResponse(
          [void Function(SolutionStatsResponseBuilder)? updates]) =>
      (SolutionStatsResponseBuilder()..update(updates))._build();

  _$SolutionStatsResponse._(
      {required this.fairness,
      required this.solutionId,
      required this.stability,
      required this.workload})
      : super._();
  @override
  SolutionStatsResponse rebuild(
          void Function(SolutionStatsResponseBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  SolutionStatsResponseBuilder toBuilder() =>
      SolutionStatsResponseBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is SolutionStatsResponse &&
        fairness == other.fairness &&
        solutionId == other.solutionId &&
        stability == other.stability &&
        workload == other.workload;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, fairness.hashCode);
    _$hash = $jc(_$hash, solutionId.hashCode);
    _$hash = $jc(_$hash, stability.hashCode);
    _$hash = $jc(_$hash, workload.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'SolutionStatsResponse')
          ..add('fairness', fairness)
          ..add('solutionId', solutionId)
          ..add('stability', stability)
          ..add('workload', workload))
        .toString();
  }
}

class SolutionStatsResponseBuilder
    implements Builder<SolutionStatsResponse, SolutionStatsResponseBuilder> {
  _$SolutionStatsResponse? _$v;

  FairnessStatsBuilder? _fairness;
  FairnessStatsBuilder get fairness =>
      _$this._fairness ??= FairnessStatsBuilder();
  set fairness(FairnessStatsBuilder? fairness) => _$this._fairness = fairness;

  int? _solutionId;
  int? get solutionId => _$this._solutionId;
  set solutionId(int? solutionId) => _$this._solutionId = solutionId;

  StabilityMetricsBuilder? _stability;
  StabilityMetricsBuilder get stability =>
      _$this._stability ??= StabilityMetricsBuilder();
  set stability(StabilityMetricsBuilder? stability) =>
      _$this._stability = stability;

  WorkloadStatsBuilder? _workload;
  WorkloadStatsBuilder get workload =>
      _$this._workload ??= WorkloadStatsBuilder();
  set workload(WorkloadStatsBuilder? workload) => _$this._workload = workload;

  SolutionStatsResponseBuilder() {
    SolutionStatsResponse._defaults(this);
  }

  SolutionStatsResponseBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _fairness = $v.fairness.toBuilder();
      _solutionId = $v.solutionId;
      _stability = $v.stability.toBuilder();
      _workload = $v.workload.toBuilder();
      _$v = null;
    }
    return this;
  }

  @override
  void replace(SolutionStatsResponse other) {
    _$v = other as _$SolutionStatsResponse;
  }

  @override
  void update(void Function(SolutionStatsResponseBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  SolutionStatsResponse build() => _build();

  _$SolutionStatsResponse _build() {
    _$SolutionStatsResponse _$result;
    try {
      _$result = _$v ??
          _$SolutionStatsResponse._(
            fairness: fairness.build(),
            solutionId: BuiltValueNullFieldError.checkNotNull(
                solutionId, r'SolutionStatsResponse', 'solutionId'),
            stability: stability.build(),
            workload: workload.build(),
          );
    } catch (_) {
      late String _$failedField;
      try {
        _$failedField = 'fairness';
        fairness.build();

        _$failedField = 'stability';
        stability.build();
        _$failedField = 'workload';
        workload.build();
      } catch (e) {
        throw BuiltValueNestedFieldError(
            r'SolutionStatsResponse', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
