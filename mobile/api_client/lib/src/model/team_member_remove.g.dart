// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'team_member_remove.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$TeamMemberRemove extends TeamMemberRemove {
  @override
  final BuiltList<String> personIds;

  factory _$TeamMemberRemove(
          [void Function(TeamMemberRemoveBuilder)? updates]) =>
      (TeamMemberRemoveBuilder()..update(updates))._build();

  _$TeamMemberRemove._({required this.personIds}) : super._();
  @override
  TeamMemberRemove rebuild(void Function(TeamMemberRemoveBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  TeamMemberRemoveBuilder toBuilder() =>
      TeamMemberRemoveBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is TeamMemberRemove && personIds == other.personIds;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, personIds.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'TeamMemberRemove')
          ..add('personIds', personIds))
        .toString();
  }
}

class TeamMemberRemoveBuilder
    implements Builder<TeamMemberRemove, TeamMemberRemoveBuilder> {
  _$TeamMemberRemove? _$v;

  ListBuilder<String>? _personIds;
  ListBuilder<String> get personIds =>
      _$this._personIds ??= ListBuilder<String>();
  set personIds(ListBuilder<String>? personIds) =>
      _$this._personIds = personIds;

  TeamMemberRemoveBuilder() {
    TeamMemberRemove._defaults(this);
  }

  TeamMemberRemoveBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _personIds = $v.personIds.toBuilder();
      _$v = null;
    }
    return this;
  }

  @override
  void replace(TeamMemberRemove other) {
    _$v = other as _$TeamMemberRemove;
  }

  @override
  void update(void Function(TeamMemberRemoveBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  TeamMemberRemove build() => _build();

  _$TeamMemberRemove _build() {
    _$TeamMemberRemove _$result;
    try {
      _$result = _$v ??
          _$TeamMemberRemove._(
            personIds: personIds.build(),
          );
    } catch (_) {
      late String _$failedField;
      try {
        _$failedField = 'personIds';
        personIds.build();
      } catch (e) {
        throw BuiltValueNestedFieldError(
            r'TeamMemberRemove', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
