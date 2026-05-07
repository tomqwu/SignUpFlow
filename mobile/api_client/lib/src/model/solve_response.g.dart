// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'solve_response.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$SolveResponse extends SolveResponse {
  @override
  final int assignmentCount;
  @override
  final String message;
  @override
  final SolutionMetrics metrics;
  @override
  final int solutionId;
  @override
  final BuiltList<ViolationInfo> violations;

  factory _$SolveResponse([void Function(SolveResponseBuilder)? updates]) =>
      (SolveResponseBuilder()..update(updates))._build();

  _$SolveResponse._(
      {required this.assignmentCount,
      required this.message,
      required this.metrics,
      required this.solutionId,
      required this.violations})
      : super._();
  @override
  SolveResponse rebuild(void Function(SolveResponseBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  SolveResponseBuilder toBuilder() => SolveResponseBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is SolveResponse &&
        assignmentCount == other.assignmentCount &&
        message == other.message &&
        metrics == other.metrics &&
        solutionId == other.solutionId &&
        violations == other.violations;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, assignmentCount.hashCode);
    _$hash = $jc(_$hash, message.hashCode);
    _$hash = $jc(_$hash, metrics.hashCode);
    _$hash = $jc(_$hash, solutionId.hashCode);
    _$hash = $jc(_$hash, violations.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'SolveResponse')
          ..add('assignmentCount', assignmentCount)
          ..add('message', message)
          ..add('metrics', metrics)
          ..add('solutionId', solutionId)
          ..add('violations', violations))
        .toString();
  }
}

class SolveResponseBuilder
    implements Builder<SolveResponse, SolveResponseBuilder> {
  _$SolveResponse? _$v;

  int? _assignmentCount;
  int? get assignmentCount => _$this._assignmentCount;
  set assignmentCount(int? assignmentCount) =>
      _$this._assignmentCount = assignmentCount;

  String? _message;
  String? get message => _$this._message;
  set message(String? message) => _$this._message = message;

  SolutionMetricsBuilder? _metrics;
  SolutionMetricsBuilder get metrics =>
      _$this._metrics ??= SolutionMetricsBuilder();
  set metrics(SolutionMetricsBuilder? metrics) => _$this._metrics = metrics;

  int? _solutionId;
  int? get solutionId => _$this._solutionId;
  set solutionId(int? solutionId) => _$this._solutionId = solutionId;

  ListBuilder<ViolationInfo>? _violations;
  ListBuilder<ViolationInfo> get violations =>
      _$this._violations ??= ListBuilder<ViolationInfo>();
  set violations(ListBuilder<ViolationInfo>? violations) =>
      _$this._violations = violations;

  SolveResponseBuilder() {
    SolveResponse._defaults(this);
  }

  SolveResponseBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _assignmentCount = $v.assignmentCount;
      _message = $v.message;
      _metrics = $v.metrics.toBuilder();
      _solutionId = $v.solutionId;
      _violations = $v.violations.toBuilder();
      _$v = null;
    }
    return this;
  }

  @override
  void replace(SolveResponse other) {
    _$v = other as _$SolveResponse;
  }

  @override
  void update(void Function(SolveResponseBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  SolveResponse build() => _build();

  _$SolveResponse _build() {
    _$SolveResponse _$result;
    try {
      _$result = _$v ??
          _$SolveResponse._(
            assignmentCount: BuiltValueNullFieldError.checkNotNull(
                assignmentCount, r'SolveResponse', 'assignmentCount'),
            message: BuiltValueNullFieldError.checkNotNull(
                message, r'SolveResponse', 'message'),
            metrics: metrics.build(),
            solutionId: BuiltValueNullFieldError.checkNotNull(
                solutionId, r'SolveResponse', 'solutionId'),
            violations: violations.build(),
          );
    } catch (_) {
      late String _$failedField;
      try {
        _$failedField = 'metrics';
        metrics.build();

        _$failedField = 'violations';
        violations.build();
      } catch (e) {
        throw BuiltValueNestedFieldError(
            r'SolveResponse', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
