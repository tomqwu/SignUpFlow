// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'conflict_check_response.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$ConflictCheckResponse extends ConflictCheckResponse {
  @override
  final bool canAssign;
  @override
  final BuiltList<ConflictType>? conflicts;
  @override
  final bool hasConflicts;

  factory _$ConflictCheckResponse(
          [void Function(ConflictCheckResponseBuilder)? updates]) =>
      (ConflictCheckResponseBuilder()..update(updates))._build();

  _$ConflictCheckResponse._(
      {required this.canAssign, this.conflicts, required this.hasConflicts})
      : super._();
  @override
  ConflictCheckResponse rebuild(
          void Function(ConflictCheckResponseBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  ConflictCheckResponseBuilder toBuilder() =>
      ConflictCheckResponseBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is ConflictCheckResponse &&
        canAssign == other.canAssign &&
        conflicts == other.conflicts &&
        hasConflicts == other.hasConflicts;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, canAssign.hashCode);
    _$hash = $jc(_$hash, conflicts.hashCode);
    _$hash = $jc(_$hash, hasConflicts.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'ConflictCheckResponse')
          ..add('canAssign', canAssign)
          ..add('conflicts', conflicts)
          ..add('hasConflicts', hasConflicts))
        .toString();
  }
}

class ConflictCheckResponseBuilder
    implements Builder<ConflictCheckResponse, ConflictCheckResponseBuilder> {
  _$ConflictCheckResponse? _$v;

  bool? _canAssign;
  bool? get canAssign => _$this._canAssign;
  set canAssign(bool? canAssign) => _$this._canAssign = canAssign;

  ListBuilder<ConflictType>? _conflicts;
  ListBuilder<ConflictType> get conflicts =>
      _$this._conflicts ??= ListBuilder<ConflictType>();
  set conflicts(ListBuilder<ConflictType>? conflicts) =>
      _$this._conflicts = conflicts;

  bool? _hasConflicts;
  bool? get hasConflicts => _$this._hasConflicts;
  set hasConflicts(bool? hasConflicts) => _$this._hasConflicts = hasConflicts;

  ConflictCheckResponseBuilder() {
    ConflictCheckResponse._defaults(this);
  }

  ConflictCheckResponseBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _canAssign = $v.canAssign;
      _conflicts = $v.conflicts?.toBuilder();
      _hasConflicts = $v.hasConflicts;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(ConflictCheckResponse other) {
    _$v = other as _$ConflictCheckResponse;
  }

  @override
  void update(void Function(ConflictCheckResponseBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  ConflictCheckResponse build() => _build();

  _$ConflictCheckResponse _build() {
    _$ConflictCheckResponse _$result;
    try {
      _$result = _$v ??
          _$ConflictCheckResponse._(
            canAssign: BuiltValueNullFieldError.checkNotNull(
                canAssign, r'ConflictCheckResponse', 'canAssign'),
            conflicts: _conflicts?.build(),
            hasConflicts: BuiltValueNullFieldError.checkNotNull(
                hasConflicts, r'ConflictCheckResponse', 'hasConflicts'),
          );
    } catch (_) {
      late String _$failedField;
      try {
        _$failedField = 'conflicts';
        _conflicts?.build();
      } catch (e) {
        throw BuiltValueNestedFieldError(
            r'ConflictCheckResponse', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
