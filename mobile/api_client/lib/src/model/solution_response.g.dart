// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'solution_response.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$SolutionResponse extends SolutionResponse {
  @override
  final int? assignmentCount;
  @override
  final DateTime createdAt;
  @override
  final int hardViolations;
  @override
  final num healthScore;
  @override
  final int id;
  @override
  final bool? isPublished;
  @override
  final BuiltMap<String, JsonObject?>? metrics;
  @override
  final String orgId;
  @override
  final DateTime? publishedAt;
  @override
  final Date? scopeEnd;
  @override
  final BuiltList<String>? scopeEventIds;
  @override
  final String? scopeFingerprint;
  @override
  final Date? scopeStart;
  @override
  final num softScore;
  @override
  final num solveMs;

  factory _$SolutionResponse(
          [void Function(SolutionResponseBuilder)? updates]) =>
      (SolutionResponseBuilder()..update(updates))._build();

  _$SolutionResponse._(
      {this.assignmentCount,
      required this.createdAt,
      required this.hardViolations,
      required this.healthScore,
      required this.id,
      this.isPublished,
      this.metrics,
      required this.orgId,
      this.publishedAt,
      this.scopeEnd,
      this.scopeEventIds,
      this.scopeFingerprint,
      this.scopeStart,
      required this.softScore,
      required this.solveMs})
      : super._();
  @override
  SolutionResponse rebuild(void Function(SolutionResponseBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  SolutionResponseBuilder toBuilder() =>
      SolutionResponseBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is SolutionResponse &&
        assignmentCount == other.assignmentCount &&
        createdAt == other.createdAt &&
        hardViolations == other.hardViolations &&
        healthScore == other.healthScore &&
        id == other.id &&
        isPublished == other.isPublished &&
        metrics == other.metrics &&
        orgId == other.orgId &&
        publishedAt == other.publishedAt &&
        scopeEnd == other.scopeEnd &&
        scopeEventIds == other.scopeEventIds &&
        scopeFingerprint == other.scopeFingerprint &&
        scopeStart == other.scopeStart &&
        softScore == other.softScore &&
        solveMs == other.solveMs;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, assignmentCount.hashCode);
    _$hash = $jc(_$hash, createdAt.hashCode);
    _$hash = $jc(_$hash, hardViolations.hashCode);
    _$hash = $jc(_$hash, healthScore.hashCode);
    _$hash = $jc(_$hash, id.hashCode);
    _$hash = $jc(_$hash, isPublished.hashCode);
    _$hash = $jc(_$hash, metrics.hashCode);
    _$hash = $jc(_$hash, orgId.hashCode);
    _$hash = $jc(_$hash, publishedAt.hashCode);
    _$hash = $jc(_$hash, scopeEnd.hashCode);
    _$hash = $jc(_$hash, scopeEventIds.hashCode);
    _$hash = $jc(_$hash, scopeFingerprint.hashCode);
    _$hash = $jc(_$hash, scopeStart.hashCode);
    _$hash = $jc(_$hash, softScore.hashCode);
    _$hash = $jc(_$hash, solveMs.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'SolutionResponse')
          ..add('assignmentCount', assignmentCount)
          ..add('createdAt', createdAt)
          ..add('hardViolations', hardViolations)
          ..add('healthScore', healthScore)
          ..add('id', id)
          ..add('isPublished', isPublished)
          ..add('metrics', metrics)
          ..add('orgId', orgId)
          ..add('publishedAt', publishedAt)
          ..add('scopeEnd', scopeEnd)
          ..add('scopeEventIds', scopeEventIds)
          ..add('scopeFingerprint', scopeFingerprint)
          ..add('scopeStart', scopeStart)
          ..add('softScore', softScore)
          ..add('solveMs', solveMs))
        .toString();
  }
}

class SolutionResponseBuilder
    implements Builder<SolutionResponse, SolutionResponseBuilder> {
  _$SolutionResponse? _$v;

  int? _assignmentCount;
  int? get assignmentCount => _$this._assignmentCount;
  set assignmentCount(int? assignmentCount) =>
      _$this._assignmentCount = assignmentCount;

  DateTime? _createdAt;
  DateTime? get createdAt => _$this._createdAt;
  set createdAt(DateTime? createdAt) => _$this._createdAt = createdAt;

  int? _hardViolations;
  int? get hardViolations => _$this._hardViolations;
  set hardViolations(int? hardViolations) =>
      _$this._hardViolations = hardViolations;

  num? _healthScore;
  num? get healthScore => _$this._healthScore;
  set healthScore(num? healthScore) => _$this._healthScore = healthScore;

  int? _id;
  int? get id => _$this._id;
  set id(int? id) => _$this._id = id;

  bool? _isPublished;
  bool? get isPublished => _$this._isPublished;
  set isPublished(bool? isPublished) => _$this._isPublished = isPublished;

  MapBuilder<String, JsonObject?>? _metrics;
  MapBuilder<String, JsonObject?> get metrics =>
      _$this._metrics ??= MapBuilder<String, JsonObject?>();
  set metrics(MapBuilder<String, JsonObject?>? metrics) =>
      _$this._metrics = metrics;

  String? _orgId;
  String? get orgId => _$this._orgId;
  set orgId(String? orgId) => _$this._orgId = orgId;

  DateTime? _publishedAt;
  DateTime? get publishedAt => _$this._publishedAt;
  set publishedAt(DateTime? publishedAt) => _$this._publishedAt = publishedAt;

  Date? _scopeEnd;
  Date? get scopeEnd => _$this._scopeEnd;
  set scopeEnd(Date? scopeEnd) => _$this._scopeEnd = scopeEnd;

  ListBuilder<String>? _scopeEventIds;
  ListBuilder<String> get scopeEventIds =>
      _$this._scopeEventIds ??= ListBuilder<String>();
  set scopeEventIds(ListBuilder<String>? scopeEventIds) =>
      _$this._scopeEventIds = scopeEventIds;

  String? _scopeFingerprint;
  String? get scopeFingerprint => _$this._scopeFingerprint;
  set scopeFingerprint(String? scopeFingerprint) =>
      _$this._scopeFingerprint = scopeFingerprint;

  Date? _scopeStart;
  Date? get scopeStart => _$this._scopeStart;
  set scopeStart(Date? scopeStart) => _$this._scopeStart = scopeStart;

  num? _softScore;
  num? get softScore => _$this._softScore;
  set softScore(num? softScore) => _$this._softScore = softScore;

  num? _solveMs;
  num? get solveMs => _$this._solveMs;
  set solveMs(num? solveMs) => _$this._solveMs = solveMs;

  SolutionResponseBuilder() {
    SolutionResponse._defaults(this);
  }

  SolutionResponseBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _assignmentCount = $v.assignmentCount;
      _createdAt = $v.createdAt;
      _hardViolations = $v.hardViolations;
      _healthScore = $v.healthScore;
      _id = $v.id;
      _isPublished = $v.isPublished;
      _metrics = $v.metrics?.toBuilder();
      _orgId = $v.orgId;
      _publishedAt = $v.publishedAt;
      _scopeEnd = $v.scopeEnd;
      _scopeEventIds = $v.scopeEventIds?.toBuilder();
      _scopeFingerprint = $v.scopeFingerprint;
      _scopeStart = $v.scopeStart;
      _softScore = $v.softScore;
      _solveMs = $v.solveMs;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(SolutionResponse other) {
    _$v = other as _$SolutionResponse;
  }

  @override
  void update(void Function(SolutionResponseBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  SolutionResponse build() => _build();

  _$SolutionResponse _build() {
    _$SolutionResponse _$result;
    try {
      _$result = _$v ??
          _$SolutionResponse._(
            assignmentCount: assignmentCount,
            createdAt: BuiltValueNullFieldError.checkNotNull(
                createdAt, r'SolutionResponse', 'createdAt'),
            hardViolations: BuiltValueNullFieldError.checkNotNull(
                hardViolations, r'SolutionResponse', 'hardViolations'),
            healthScore: BuiltValueNullFieldError.checkNotNull(
                healthScore, r'SolutionResponse', 'healthScore'),
            id: BuiltValueNullFieldError.checkNotNull(
                id, r'SolutionResponse', 'id'),
            isPublished: isPublished,
            metrics: _metrics?.build(),
            orgId: BuiltValueNullFieldError.checkNotNull(
                orgId, r'SolutionResponse', 'orgId'),
            publishedAt: publishedAt,
            scopeEnd: scopeEnd,
            scopeEventIds: _scopeEventIds?.build(),
            scopeFingerprint: scopeFingerprint,
            scopeStart: scopeStart,
            softScore: BuiltValueNullFieldError.checkNotNull(
                softScore, r'SolutionResponse', 'softScore'),
            solveMs: BuiltValueNullFieldError.checkNotNull(
                solveMs, r'SolutionResponse', 'solveMs'),
          );
    } catch (_) {
      late String _$failedField;
      try {
        _$failedField = 'metrics';
        _metrics?.build();

        _$failedField = 'scopeEventIds';
        _scopeEventIds?.build();
      } catch (e) {
        throw BuiltValueNestedFieldError(
            r'SolutionResponse', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
