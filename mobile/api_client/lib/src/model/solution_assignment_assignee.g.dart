// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'solution_assignment_assignee.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$SolutionAssignmentAssignee extends SolutionAssignmentAssignee {
  @override
  final DateTime? assignedAt;
  @override
  final int assignmentId;
  @override
  final String personId;
  @override
  final String? personName;

  factory _$SolutionAssignmentAssignee(
          [void Function(SolutionAssignmentAssigneeBuilder)? updates]) =>
      (SolutionAssignmentAssigneeBuilder()..update(updates))._build();

  _$SolutionAssignmentAssignee._(
      {this.assignedAt,
      required this.assignmentId,
      required this.personId,
      this.personName})
      : super._();
  @override
  SolutionAssignmentAssignee rebuild(
          void Function(SolutionAssignmentAssigneeBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  SolutionAssignmentAssigneeBuilder toBuilder() =>
      SolutionAssignmentAssigneeBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is SolutionAssignmentAssignee &&
        assignedAt == other.assignedAt &&
        assignmentId == other.assignmentId &&
        personId == other.personId &&
        personName == other.personName;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, assignedAt.hashCode);
    _$hash = $jc(_$hash, assignmentId.hashCode);
    _$hash = $jc(_$hash, personId.hashCode);
    _$hash = $jc(_$hash, personName.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'SolutionAssignmentAssignee')
          ..add('assignedAt', assignedAt)
          ..add('assignmentId', assignmentId)
          ..add('personId', personId)
          ..add('personName', personName))
        .toString();
  }
}

class SolutionAssignmentAssigneeBuilder
    implements
        Builder<SolutionAssignmentAssignee, SolutionAssignmentAssigneeBuilder> {
  _$SolutionAssignmentAssignee? _$v;

  DateTime? _assignedAt;
  DateTime? get assignedAt => _$this._assignedAt;
  set assignedAt(DateTime? assignedAt) => _$this._assignedAt = assignedAt;

  int? _assignmentId;
  int? get assignmentId => _$this._assignmentId;
  set assignmentId(int? assignmentId) => _$this._assignmentId = assignmentId;

  String? _personId;
  String? get personId => _$this._personId;
  set personId(String? personId) => _$this._personId = personId;

  String? _personName;
  String? get personName => _$this._personName;
  set personName(String? personName) => _$this._personName = personName;

  SolutionAssignmentAssigneeBuilder() {
    SolutionAssignmentAssignee._defaults(this);
  }

  SolutionAssignmentAssigneeBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _assignedAt = $v.assignedAt;
      _assignmentId = $v.assignmentId;
      _personId = $v.personId;
      _personName = $v.personName;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(SolutionAssignmentAssignee other) {
    _$v = other as _$SolutionAssignmentAssignee;
  }

  @override
  void update(void Function(SolutionAssignmentAssigneeBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  SolutionAssignmentAssignee build() => _build();

  _$SolutionAssignmentAssignee _build() {
    final _$result = _$v ??
        _$SolutionAssignmentAssignee._(
          assignedAt: assignedAt,
          assignmentId: BuiltValueNullFieldError.checkNotNull(
              assignmentId, r'SolutionAssignmentAssignee', 'assignmentId'),
          personId: BuiltValueNullFieldError.checkNotNull(
              personId, r'SolutionAssignmentAssignee', 'personId'),
          personName: personName,
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
