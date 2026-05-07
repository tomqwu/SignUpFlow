// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'assignment_decline_request.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$AssignmentDeclineRequest extends AssignmentDeclineRequest {
  @override
  final String declineReason;

  factory _$AssignmentDeclineRequest(
          [void Function(AssignmentDeclineRequestBuilder)? updates]) =>
      (AssignmentDeclineRequestBuilder()..update(updates))._build();

  _$AssignmentDeclineRequest._({required this.declineReason}) : super._();
  @override
  AssignmentDeclineRequest rebuild(
          void Function(AssignmentDeclineRequestBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  AssignmentDeclineRequestBuilder toBuilder() =>
      AssignmentDeclineRequestBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is AssignmentDeclineRequest &&
        declineReason == other.declineReason;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, declineReason.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'AssignmentDeclineRequest')
          ..add('declineReason', declineReason))
        .toString();
  }
}

class AssignmentDeclineRequestBuilder
    implements
        Builder<AssignmentDeclineRequest, AssignmentDeclineRequestBuilder> {
  _$AssignmentDeclineRequest? _$v;

  String? _declineReason;
  String? get declineReason => _$this._declineReason;
  set declineReason(String? declineReason) =>
      _$this._declineReason = declineReason;

  AssignmentDeclineRequestBuilder() {
    AssignmentDeclineRequest._defaults(this);
  }

  AssignmentDeclineRequestBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _declineReason = $v.declineReason;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(AssignmentDeclineRequest other) {
    _$v = other as _$AssignmentDeclineRequest;
  }

  @override
  void update(void Function(AssignmentDeclineRequestBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  AssignmentDeclineRequest build() => _build();

  _$AssignmentDeclineRequest _build() {
    final _$result = _$v ??
        _$AssignmentDeclineRequest._(
          declineReason: BuiltValueNullFieldError.checkNotNull(
              declineReason, r'AssignmentDeclineRequest', 'declineReason'),
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
