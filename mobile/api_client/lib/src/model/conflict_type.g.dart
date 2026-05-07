// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'conflict_type.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$ConflictType extends ConflictType {
  @override
  final String? conflictingEventId;
  @override
  final DateTime? endTime;
  @override
  final String message;
  @override
  final DateTime? startTime;
  @override
  final String type;

  factory _$ConflictType([void Function(ConflictTypeBuilder)? updates]) =>
      (ConflictTypeBuilder()..update(updates))._build();

  _$ConflictType._(
      {this.conflictingEventId,
      this.endTime,
      required this.message,
      this.startTime,
      required this.type})
      : super._();
  @override
  ConflictType rebuild(void Function(ConflictTypeBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  ConflictTypeBuilder toBuilder() => ConflictTypeBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is ConflictType &&
        conflictingEventId == other.conflictingEventId &&
        endTime == other.endTime &&
        message == other.message &&
        startTime == other.startTime &&
        type == other.type;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, conflictingEventId.hashCode);
    _$hash = $jc(_$hash, endTime.hashCode);
    _$hash = $jc(_$hash, message.hashCode);
    _$hash = $jc(_$hash, startTime.hashCode);
    _$hash = $jc(_$hash, type.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'ConflictType')
          ..add('conflictingEventId', conflictingEventId)
          ..add('endTime', endTime)
          ..add('message', message)
          ..add('startTime', startTime)
          ..add('type', type))
        .toString();
  }
}

class ConflictTypeBuilder
    implements Builder<ConflictType, ConflictTypeBuilder> {
  _$ConflictType? _$v;

  String? _conflictingEventId;
  String? get conflictingEventId => _$this._conflictingEventId;
  set conflictingEventId(String? conflictingEventId) =>
      _$this._conflictingEventId = conflictingEventId;

  DateTime? _endTime;
  DateTime? get endTime => _$this._endTime;
  set endTime(DateTime? endTime) => _$this._endTime = endTime;

  String? _message;
  String? get message => _$this._message;
  set message(String? message) => _$this._message = message;

  DateTime? _startTime;
  DateTime? get startTime => _$this._startTime;
  set startTime(DateTime? startTime) => _$this._startTime = startTime;

  String? _type;
  String? get type => _$this._type;
  set type(String? type) => _$this._type = type;

  ConflictTypeBuilder() {
    ConflictType._defaults(this);
  }

  ConflictTypeBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _conflictingEventId = $v.conflictingEventId;
      _endTime = $v.endTime;
      _message = $v.message;
      _startTime = $v.startTime;
      _type = $v.type;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(ConflictType other) {
    _$v = other as _$ConflictType;
  }

  @override
  void update(void Function(ConflictTypeBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  ConflictType build() => _build();

  _$ConflictType _build() {
    final _$result = _$v ??
        _$ConflictType._(
          conflictingEventId: conflictingEventId,
          endTime: endTime,
          message: BuiltValueNullFieldError.checkNotNull(
              message, r'ConflictType', 'message'),
          startTime: startTime,
          type: BuiltValueNullFieldError.checkNotNull(
              type, r'ConflictType', 'type'),
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
