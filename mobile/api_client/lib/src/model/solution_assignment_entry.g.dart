// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'solution_assignment_entry.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$SolutionAssignmentEntry extends SolutionAssignmentEntry {
  @override
  final BuiltList<SolutionAssignmentAssignee> assignees;
  @override
  final DateTime? eventEnd;
  @override
  final String eventId;
  @override
  final DateTime? eventStart;
  @override
  final String? eventType;

  factory _$SolutionAssignmentEntry(
          [void Function(SolutionAssignmentEntryBuilder)? updates]) =>
      (SolutionAssignmentEntryBuilder()..update(updates))._build();

  _$SolutionAssignmentEntry._(
      {required this.assignees,
      this.eventEnd,
      required this.eventId,
      this.eventStart,
      this.eventType})
      : super._();
  @override
  SolutionAssignmentEntry rebuild(
          void Function(SolutionAssignmentEntryBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  SolutionAssignmentEntryBuilder toBuilder() =>
      SolutionAssignmentEntryBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is SolutionAssignmentEntry &&
        assignees == other.assignees &&
        eventEnd == other.eventEnd &&
        eventId == other.eventId &&
        eventStart == other.eventStart &&
        eventType == other.eventType;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, assignees.hashCode);
    _$hash = $jc(_$hash, eventEnd.hashCode);
    _$hash = $jc(_$hash, eventId.hashCode);
    _$hash = $jc(_$hash, eventStart.hashCode);
    _$hash = $jc(_$hash, eventType.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'SolutionAssignmentEntry')
          ..add('assignees', assignees)
          ..add('eventEnd', eventEnd)
          ..add('eventId', eventId)
          ..add('eventStart', eventStart)
          ..add('eventType', eventType))
        .toString();
  }
}

class SolutionAssignmentEntryBuilder
    implements
        Builder<SolutionAssignmentEntry, SolutionAssignmentEntryBuilder> {
  _$SolutionAssignmentEntry? _$v;

  ListBuilder<SolutionAssignmentAssignee>? _assignees;
  ListBuilder<SolutionAssignmentAssignee> get assignees =>
      _$this._assignees ??= ListBuilder<SolutionAssignmentAssignee>();
  set assignees(ListBuilder<SolutionAssignmentAssignee>? assignees) =>
      _$this._assignees = assignees;

  DateTime? _eventEnd;
  DateTime? get eventEnd => _$this._eventEnd;
  set eventEnd(DateTime? eventEnd) => _$this._eventEnd = eventEnd;

  String? _eventId;
  String? get eventId => _$this._eventId;
  set eventId(String? eventId) => _$this._eventId = eventId;

  DateTime? _eventStart;
  DateTime? get eventStart => _$this._eventStart;
  set eventStart(DateTime? eventStart) => _$this._eventStart = eventStart;

  String? _eventType;
  String? get eventType => _$this._eventType;
  set eventType(String? eventType) => _$this._eventType = eventType;

  SolutionAssignmentEntryBuilder() {
    SolutionAssignmentEntry._defaults(this);
  }

  SolutionAssignmentEntryBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _assignees = $v.assignees.toBuilder();
      _eventEnd = $v.eventEnd;
      _eventId = $v.eventId;
      _eventStart = $v.eventStart;
      _eventType = $v.eventType;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(SolutionAssignmentEntry other) {
    _$v = other as _$SolutionAssignmentEntry;
  }

  @override
  void update(void Function(SolutionAssignmentEntryBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  SolutionAssignmentEntry build() => _build();

  _$SolutionAssignmentEntry _build() {
    _$SolutionAssignmentEntry _$result;
    try {
      _$result = _$v ??
          _$SolutionAssignmentEntry._(
            assignees: assignees.build(),
            eventEnd: eventEnd,
            eventId: BuiltValueNullFieldError.checkNotNull(
                eventId, r'SolutionAssignmentEntry', 'eventId'),
            eventStart: eventStart,
            eventType: eventType,
          );
    } catch (_) {
      late String _$failedField;
      try {
        _$failedField = 'assignees';
        assignees.build();
      } catch (e) {
        throw BuiltValueNestedFieldError(
            r'SolutionAssignmentEntry', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
