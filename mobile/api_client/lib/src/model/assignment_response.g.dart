// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'assignment_response.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$AssignmentResponse extends AssignmentResponse {
  @override
  final DateTime assignedAt;
  @override
  final String? declineReason;
  @override
  final String eventId;
  @override
  final int id;
  @override
  final String personId;
  @override
  final String? role;
  @override
  final String status;

  factory _$AssignmentResponse(
          [void Function(AssignmentResponseBuilder)? updates]) =>
      (AssignmentResponseBuilder()..update(updates))._build();

  _$AssignmentResponse._(
      {required this.assignedAt,
      this.declineReason,
      required this.eventId,
      required this.id,
      required this.personId,
      this.role,
      required this.status})
      : super._();
  @override
  AssignmentResponse rebuild(
          void Function(AssignmentResponseBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  AssignmentResponseBuilder toBuilder() =>
      AssignmentResponseBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is AssignmentResponse &&
        assignedAt == other.assignedAt &&
        declineReason == other.declineReason &&
        eventId == other.eventId &&
        id == other.id &&
        personId == other.personId &&
        role == other.role &&
        status == other.status;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, assignedAt.hashCode);
    _$hash = $jc(_$hash, declineReason.hashCode);
    _$hash = $jc(_$hash, eventId.hashCode);
    _$hash = $jc(_$hash, id.hashCode);
    _$hash = $jc(_$hash, personId.hashCode);
    _$hash = $jc(_$hash, role.hashCode);
    _$hash = $jc(_$hash, status.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'AssignmentResponse')
          ..add('assignedAt', assignedAt)
          ..add('declineReason', declineReason)
          ..add('eventId', eventId)
          ..add('id', id)
          ..add('personId', personId)
          ..add('role', role)
          ..add('status', status))
        .toString();
  }
}

class AssignmentResponseBuilder
    implements Builder<AssignmentResponse, AssignmentResponseBuilder> {
  _$AssignmentResponse? _$v;

  DateTime? _assignedAt;
  DateTime? get assignedAt => _$this._assignedAt;
  set assignedAt(DateTime? assignedAt) => _$this._assignedAt = assignedAt;

  String? _declineReason;
  String? get declineReason => _$this._declineReason;
  set declineReason(String? declineReason) =>
      _$this._declineReason = declineReason;

  String? _eventId;
  String? get eventId => _$this._eventId;
  set eventId(String? eventId) => _$this._eventId = eventId;

  int? _id;
  int? get id => _$this._id;
  set id(int? id) => _$this._id = id;

  String? _personId;
  String? get personId => _$this._personId;
  set personId(String? personId) => _$this._personId = personId;

  String? _role;
  String? get role => _$this._role;
  set role(String? role) => _$this._role = role;

  String? _status;
  String? get status => _$this._status;
  set status(String? status) => _$this._status = status;

  AssignmentResponseBuilder() {
    AssignmentResponse._defaults(this);
  }

  AssignmentResponseBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _assignedAt = $v.assignedAt;
      _declineReason = $v.declineReason;
      _eventId = $v.eventId;
      _id = $v.id;
      _personId = $v.personId;
      _role = $v.role;
      _status = $v.status;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(AssignmentResponse other) {
    _$v = other as _$AssignmentResponse;
  }

  @override
  void update(void Function(AssignmentResponseBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  AssignmentResponse build() => _build();

  _$AssignmentResponse _build() {
    final _$result = _$v ??
        _$AssignmentResponse._(
          assignedAt: BuiltValueNullFieldError.checkNotNull(
              assignedAt, r'AssignmentResponse', 'assignedAt'),
          declineReason: declineReason,
          eventId: BuiltValueNullFieldError.checkNotNull(
              eventId, r'AssignmentResponse', 'eventId'),
          id: BuiltValueNullFieldError.checkNotNull(
              id, r'AssignmentResponse', 'id'),
          personId: BuiltValueNullFieldError.checkNotNull(
              personId, r'AssignmentResponse', 'personId'),
          role: role,
          status: BuiltValueNullFieldError.checkNotNull(
              status, r'AssignmentResponse', 'status'),
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
