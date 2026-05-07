// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'solution_diff_response.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$SolutionDiffResponse extends SolutionDiffResponse {
  @override
  final BuiltList<AssignmentChange> added;
  @override
  final BuiltList<String> affectedPersons;
  @override
  final int moves;
  @override
  final BuiltList<AssignmentChange> removed;
  @override
  final int solutionAId;
  @override
  final int solutionBId;
  @override
  final int unchangedCount;

  factory _$SolutionDiffResponse(
          [void Function(SolutionDiffResponseBuilder)? updates]) =>
      (SolutionDiffResponseBuilder()..update(updates))._build();

  _$SolutionDiffResponse._(
      {required this.added,
      required this.affectedPersons,
      required this.moves,
      required this.removed,
      required this.solutionAId,
      required this.solutionBId,
      required this.unchangedCount})
      : super._();
  @override
  SolutionDiffResponse rebuild(
          void Function(SolutionDiffResponseBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  SolutionDiffResponseBuilder toBuilder() =>
      SolutionDiffResponseBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is SolutionDiffResponse &&
        added == other.added &&
        affectedPersons == other.affectedPersons &&
        moves == other.moves &&
        removed == other.removed &&
        solutionAId == other.solutionAId &&
        solutionBId == other.solutionBId &&
        unchangedCount == other.unchangedCount;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, added.hashCode);
    _$hash = $jc(_$hash, affectedPersons.hashCode);
    _$hash = $jc(_$hash, moves.hashCode);
    _$hash = $jc(_$hash, removed.hashCode);
    _$hash = $jc(_$hash, solutionAId.hashCode);
    _$hash = $jc(_$hash, solutionBId.hashCode);
    _$hash = $jc(_$hash, unchangedCount.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'SolutionDiffResponse')
          ..add('added', added)
          ..add('affectedPersons', affectedPersons)
          ..add('moves', moves)
          ..add('removed', removed)
          ..add('solutionAId', solutionAId)
          ..add('solutionBId', solutionBId)
          ..add('unchangedCount', unchangedCount))
        .toString();
  }
}

class SolutionDiffResponseBuilder
    implements Builder<SolutionDiffResponse, SolutionDiffResponseBuilder> {
  _$SolutionDiffResponse? _$v;

  ListBuilder<AssignmentChange>? _added;
  ListBuilder<AssignmentChange> get added =>
      _$this._added ??= ListBuilder<AssignmentChange>();
  set added(ListBuilder<AssignmentChange>? added) => _$this._added = added;

  ListBuilder<String>? _affectedPersons;
  ListBuilder<String> get affectedPersons =>
      _$this._affectedPersons ??= ListBuilder<String>();
  set affectedPersons(ListBuilder<String>? affectedPersons) =>
      _$this._affectedPersons = affectedPersons;

  int? _moves;
  int? get moves => _$this._moves;
  set moves(int? moves) => _$this._moves = moves;

  ListBuilder<AssignmentChange>? _removed;
  ListBuilder<AssignmentChange> get removed =>
      _$this._removed ??= ListBuilder<AssignmentChange>();
  set removed(ListBuilder<AssignmentChange>? removed) =>
      _$this._removed = removed;

  int? _solutionAId;
  int? get solutionAId => _$this._solutionAId;
  set solutionAId(int? solutionAId) => _$this._solutionAId = solutionAId;

  int? _solutionBId;
  int? get solutionBId => _$this._solutionBId;
  set solutionBId(int? solutionBId) => _$this._solutionBId = solutionBId;

  int? _unchangedCount;
  int? get unchangedCount => _$this._unchangedCount;
  set unchangedCount(int? unchangedCount) =>
      _$this._unchangedCount = unchangedCount;

  SolutionDiffResponseBuilder() {
    SolutionDiffResponse._defaults(this);
  }

  SolutionDiffResponseBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _added = $v.added.toBuilder();
      _affectedPersons = $v.affectedPersons.toBuilder();
      _moves = $v.moves;
      _removed = $v.removed.toBuilder();
      _solutionAId = $v.solutionAId;
      _solutionBId = $v.solutionBId;
      _unchangedCount = $v.unchangedCount;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(SolutionDiffResponse other) {
    _$v = other as _$SolutionDiffResponse;
  }

  @override
  void update(void Function(SolutionDiffResponseBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  SolutionDiffResponse build() => _build();

  _$SolutionDiffResponse _build() {
    _$SolutionDiffResponse _$result;
    try {
      _$result = _$v ??
          _$SolutionDiffResponse._(
            added: added.build(),
            affectedPersons: affectedPersons.build(),
            moves: BuiltValueNullFieldError.checkNotNull(
                moves, r'SolutionDiffResponse', 'moves'),
            removed: removed.build(),
            solutionAId: BuiltValueNullFieldError.checkNotNull(
                solutionAId, r'SolutionDiffResponse', 'solutionAId'),
            solutionBId: BuiltValueNullFieldError.checkNotNull(
                solutionBId, r'SolutionDiffResponse', 'solutionBId'),
            unchangedCount: BuiltValueNullFieldError.checkNotNull(
                unchangedCount, r'SolutionDiffResponse', 'unchangedCount'),
          );
    } catch (_) {
      late String _$failedField;
      try {
        _$failedField = 'added';
        added.build();
        _$failedField = 'affectedPersons';
        affectedPersons.build();

        _$failedField = 'removed';
        removed.build();
      } catch (e) {
        throw BuiltValueNestedFieldError(
            r'SolutionDiffResponse', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
