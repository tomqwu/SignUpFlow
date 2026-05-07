// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'assignment_change.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$AssignmentChange extends AssignmentChange {
  @override
  final String eventId;
  @override
  final String personId;
  @override
  final String? role;

  factory _$AssignmentChange(
          [void Function(AssignmentChangeBuilder)? updates]) =>
      (AssignmentChangeBuilder()..update(updates))._build();

  _$AssignmentChange._(
      {required this.eventId, required this.personId, this.role})
      : super._();
  @override
  AssignmentChange rebuild(void Function(AssignmentChangeBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  AssignmentChangeBuilder toBuilder() =>
      AssignmentChangeBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is AssignmentChange &&
        eventId == other.eventId &&
        personId == other.personId &&
        role == other.role;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, eventId.hashCode);
    _$hash = $jc(_$hash, personId.hashCode);
    _$hash = $jc(_$hash, role.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'AssignmentChange')
          ..add('eventId', eventId)
          ..add('personId', personId)
          ..add('role', role))
        .toString();
  }
}

class AssignmentChangeBuilder
    implements Builder<AssignmentChange, AssignmentChangeBuilder> {
  _$AssignmentChange? _$v;

  String? _eventId;
  String? get eventId => _$this._eventId;
  set eventId(String? eventId) => _$this._eventId = eventId;

  String? _personId;
  String? get personId => _$this._personId;
  set personId(String? personId) => _$this._personId = personId;

  String? _role;
  String? get role => _$this._role;
  set role(String? role) => _$this._role = role;

  AssignmentChangeBuilder() {
    AssignmentChange._defaults(this);
  }

  AssignmentChangeBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _eventId = $v.eventId;
      _personId = $v.personId;
      _role = $v.role;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(AssignmentChange other) {
    _$v = other as _$AssignmentChange;
  }

  @override
  void update(void Function(AssignmentChangeBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  AssignmentChange build() => _build();

  _$AssignmentChange _build() {
    final _$result = _$v ??
        _$AssignmentChange._(
          eventId: BuiltValueNullFieldError.checkNotNull(
              eventId, r'AssignmentChange', 'eventId'),
          personId: BuiltValueNullFieldError.checkNotNull(
              personId, r'AssignmentChange', 'personId'),
          role: role,
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
