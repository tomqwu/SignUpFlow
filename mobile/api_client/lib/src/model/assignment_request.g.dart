// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'assignment_request.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$AssignmentRequest extends AssignmentRequest {
  @override
  final String action;
  @override
  final String personId;
  @override
  final String? role;

  factory _$AssignmentRequest(
          [void Function(AssignmentRequestBuilder)? updates]) =>
      (AssignmentRequestBuilder()..update(updates))._build();

  _$AssignmentRequest._(
      {required this.action, required this.personId, this.role})
      : super._();
  @override
  AssignmentRequest rebuild(void Function(AssignmentRequestBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  AssignmentRequestBuilder toBuilder() =>
      AssignmentRequestBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is AssignmentRequest &&
        action == other.action &&
        personId == other.personId &&
        role == other.role;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, action.hashCode);
    _$hash = $jc(_$hash, personId.hashCode);
    _$hash = $jc(_$hash, role.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'AssignmentRequest')
          ..add('action', action)
          ..add('personId', personId)
          ..add('role', role))
        .toString();
  }
}

class AssignmentRequestBuilder
    implements Builder<AssignmentRequest, AssignmentRequestBuilder> {
  _$AssignmentRequest? _$v;

  String? _action;
  String? get action => _$this._action;
  set action(String? action) => _$this._action = action;

  String? _personId;
  String? get personId => _$this._personId;
  set personId(String? personId) => _$this._personId = personId;

  String? _role;
  String? get role => _$this._role;
  set role(String? role) => _$this._role = role;

  AssignmentRequestBuilder() {
    AssignmentRequest._defaults(this);
  }

  AssignmentRequestBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _action = $v.action;
      _personId = $v.personId;
      _role = $v.role;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(AssignmentRequest other) {
    _$v = other as _$AssignmentRequest;
  }

  @override
  void update(void Function(AssignmentRequestBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  AssignmentRequest build() => _build();

  _$AssignmentRequest _build() {
    final _$result = _$v ??
        _$AssignmentRequest._(
          action: BuiltValueNullFieldError.checkNotNull(
              action, r'AssignmentRequest', 'action'),
          personId: BuiltValueNullFieldError.checkNotNull(
              personId, r'AssignmentRequest', 'personId'),
          role: role,
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
