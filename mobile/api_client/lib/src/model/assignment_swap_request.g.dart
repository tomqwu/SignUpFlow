// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'assignment_swap_request.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$AssignmentSwapRequest extends AssignmentSwapRequest {
  @override
  final String? note;

  factory _$AssignmentSwapRequest(
          [void Function(AssignmentSwapRequestBuilder)? updates]) =>
      (AssignmentSwapRequestBuilder()..update(updates))._build();

  _$AssignmentSwapRequest._({this.note}) : super._();
  @override
  AssignmentSwapRequest rebuild(
          void Function(AssignmentSwapRequestBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  AssignmentSwapRequestBuilder toBuilder() =>
      AssignmentSwapRequestBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is AssignmentSwapRequest && note == other.note;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, note.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'AssignmentSwapRequest')
          ..add('note', note))
        .toString();
  }
}

class AssignmentSwapRequestBuilder
    implements Builder<AssignmentSwapRequest, AssignmentSwapRequestBuilder> {
  _$AssignmentSwapRequest? _$v;

  String? _note;
  String? get note => _$this._note;
  set note(String? note) => _$this._note = note;

  AssignmentSwapRequestBuilder() {
    AssignmentSwapRequest._defaults(this);
  }

  AssignmentSwapRequestBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _note = $v.note;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(AssignmentSwapRequest other) {
    _$v = other as _$AssignmentSwapRequest;
  }

  @override
  void update(void Function(AssignmentSwapRequestBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  AssignmentSwapRequest build() => _build();

  _$AssignmentSwapRequest _build() {
    final _$result = _$v ??
        _$AssignmentSwapRequest._(
          note: note,
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
