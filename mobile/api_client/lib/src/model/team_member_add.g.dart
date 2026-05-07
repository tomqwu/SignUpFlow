// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'team_member_add.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$TeamMemberAdd extends TeamMemberAdd {
  @override
  final BuiltList<String> personIds;

  factory _$TeamMemberAdd([void Function(TeamMemberAddBuilder)? updates]) =>
      (TeamMemberAddBuilder()..update(updates))._build();

  _$TeamMemberAdd._({required this.personIds}) : super._();
  @override
  TeamMemberAdd rebuild(void Function(TeamMemberAddBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  TeamMemberAddBuilder toBuilder() => TeamMemberAddBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is TeamMemberAdd && personIds == other.personIds;
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
    return (newBuiltValueToStringHelper(r'TeamMemberAdd')
          ..add('personIds', personIds))
        .toString();
  }
}

class TeamMemberAddBuilder
    implements Builder<TeamMemberAdd, TeamMemberAddBuilder> {
  _$TeamMemberAdd? _$v;

  ListBuilder<String>? _personIds;
  ListBuilder<String> get personIds =>
      _$this._personIds ??= ListBuilder<String>();
  set personIds(ListBuilder<String>? personIds) =>
      _$this._personIds = personIds;

  TeamMemberAddBuilder() {
    TeamMemberAdd._defaults(this);
  }

  TeamMemberAddBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _personIds = $v.personIds.toBuilder();
      _$v = null;
    }
    return this;
  }

  @override
  void replace(TeamMemberAdd other) {
    _$v = other as _$TeamMemberAdd;
  }

  @override
  void update(void Function(TeamMemberAddBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  TeamMemberAdd build() => _build();

  _$TeamMemberAdd _build() {
    _$TeamMemberAdd _$result;
    try {
      _$result = _$v ??
          _$TeamMemberAdd._(
            personIds: personIds.build(),
          );
    } catch (_) {
      late String _$failedField;
      try {
        _$failedField = 'personIds';
        personIds.build();
      } catch (e) {
        throw BuiltValueNestedFieldError(
            r'TeamMemberAdd', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
