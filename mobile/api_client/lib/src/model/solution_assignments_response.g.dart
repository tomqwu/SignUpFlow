// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'solution_assignments_response.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$SolutionAssignmentsResponse extends SolutionAssignmentsResponse {
  @override
  final BuiltList<SolutionAssignmentEntry> events;
  @override
  final int solutionId;
  @override
  final int totalAssignments;

  factory _$SolutionAssignmentsResponse(
          [void Function(SolutionAssignmentsResponseBuilder)? updates]) =>
      (SolutionAssignmentsResponseBuilder()..update(updates))._build();

  _$SolutionAssignmentsResponse._(
      {required this.events,
      required this.solutionId,
      required this.totalAssignments})
      : super._();
  @override
  SolutionAssignmentsResponse rebuild(
          void Function(SolutionAssignmentsResponseBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  SolutionAssignmentsResponseBuilder toBuilder() =>
      SolutionAssignmentsResponseBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is SolutionAssignmentsResponse &&
        events == other.events &&
        solutionId == other.solutionId &&
        totalAssignments == other.totalAssignments;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, events.hashCode);
    _$hash = $jc(_$hash, solutionId.hashCode);
    _$hash = $jc(_$hash, totalAssignments.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'SolutionAssignmentsResponse')
          ..add('events', events)
          ..add('solutionId', solutionId)
          ..add('totalAssignments', totalAssignments))
        .toString();
  }
}

class SolutionAssignmentsResponseBuilder
    implements
        Builder<SolutionAssignmentsResponse,
            SolutionAssignmentsResponseBuilder> {
  _$SolutionAssignmentsResponse? _$v;

  ListBuilder<SolutionAssignmentEntry>? _events;
  ListBuilder<SolutionAssignmentEntry> get events =>
      _$this._events ??= ListBuilder<SolutionAssignmentEntry>();
  set events(ListBuilder<SolutionAssignmentEntry>? events) =>
      _$this._events = events;

  int? _solutionId;
  int? get solutionId => _$this._solutionId;
  set solutionId(int? solutionId) => _$this._solutionId = solutionId;

  int? _totalAssignments;
  int? get totalAssignments => _$this._totalAssignments;
  set totalAssignments(int? totalAssignments) =>
      _$this._totalAssignments = totalAssignments;

  SolutionAssignmentsResponseBuilder() {
    SolutionAssignmentsResponse._defaults(this);
  }

  SolutionAssignmentsResponseBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _events = $v.events.toBuilder();
      _solutionId = $v.solutionId;
      _totalAssignments = $v.totalAssignments;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(SolutionAssignmentsResponse other) {
    _$v = other as _$SolutionAssignmentsResponse;
  }

  @override
  void update(void Function(SolutionAssignmentsResponseBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  SolutionAssignmentsResponse build() => _build();

  _$SolutionAssignmentsResponse _build() {
    _$SolutionAssignmentsResponse _$result;
    try {
      _$result = _$v ??
          _$SolutionAssignmentsResponse._(
            events: events.build(),
            solutionId: BuiltValueNullFieldError.checkNotNull(
                solutionId, r'SolutionAssignmentsResponse', 'solutionId'),
            totalAssignments: BuiltValueNullFieldError.checkNotNull(
                totalAssignments,
                r'SolutionAssignmentsResponse',
                'totalAssignments'),
          );
    } catch (_) {
      late String _$failedField;
      try {
        _$failedField = 'events';
        events.build();
      } catch (e) {
        throw BuiltValueNestedFieldError(
            r'SolutionAssignmentsResponse', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
