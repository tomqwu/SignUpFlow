// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'team_create.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$TeamCreate extends TeamCreate {
  @override
  final String? description;
  @override
  final BuiltMap<String, JsonObject?>? extraData;
  @override
  final String id;
  @override
  final BuiltList<String>? memberIds;
  @override
  final String name;
  @override
  final String orgId;

  factory _$TeamCreate([void Function(TeamCreateBuilder)? updates]) =>
      (TeamCreateBuilder()..update(updates))._build();

  _$TeamCreate._(
      {this.description,
      this.extraData,
      required this.id,
      this.memberIds,
      required this.name,
      required this.orgId})
      : super._();
  @override
  TeamCreate rebuild(void Function(TeamCreateBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  TeamCreateBuilder toBuilder() => TeamCreateBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is TeamCreate &&
        description == other.description &&
        extraData == other.extraData &&
        id == other.id &&
        memberIds == other.memberIds &&
        name == other.name &&
        orgId == other.orgId;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, description.hashCode);
    _$hash = $jc(_$hash, extraData.hashCode);
    _$hash = $jc(_$hash, id.hashCode);
    _$hash = $jc(_$hash, memberIds.hashCode);
    _$hash = $jc(_$hash, name.hashCode);
    _$hash = $jc(_$hash, orgId.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'TeamCreate')
          ..add('description', description)
          ..add('extraData', extraData)
          ..add('id', id)
          ..add('memberIds', memberIds)
          ..add('name', name)
          ..add('orgId', orgId))
        .toString();
  }
}

class TeamCreateBuilder implements Builder<TeamCreate, TeamCreateBuilder> {
  _$TeamCreate? _$v;

  String? _description;
  String? get description => _$this._description;
  set description(String? description) => _$this._description = description;

  MapBuilder<String, JsonObject?>? _extraData;
  MapBuilder<String, JsonObject?> get extraData =>
      _$this._extraData ??= MapBuilder<String, JsonObject?>();
  set extraData(MapBuilder<String, JsonObject?>? extraData) =>
      _$this._extraData = extraData;

  String? _id;
  String? get id => _$this._id;
  set id(String? id) => _$this._id = id;

  ListBuilder<String>? _memberIds;
  ListBuilder<String> get memberIds =>
      _$this._memberIds ??= ListBuilder<String>();
  set memberIds(ListBuilder<String>? memberIds) =>
      _$this._memberIds = memberIds;

  String? _name;
  String? get name => _$this._name;
  set name(String? name) => _$this._name = name;

  String? _orgId;
  String? get orgId => _$this._orgId;
  set orgId(String? orgId) => _$this._orgId = orgId;

  TeamCreateBuilder() {
    TeamCreate._defaults(this);
  }

  TeamCreateBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _description = $v.description;
      _extraData = $v.extraData?.toBuilder();
      _id = $v.id;
      _memberIds = $v.memberIds?.toBuilder();
      _name = $v.name;
      _orgId = $v.orgId;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(TeamCreate other) {
    _$v = other as _$TeamCreate;
  }

  @override
  void update(void Function(TeamCreateBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  TeamCreate build() => _build();

  _$TeamCreate _build() {
    _$TeamCreate _$result;
    try {
      _$result = _$v ??
          _$TeamCreate._(
            description: description,
            extraData: _extraData?.build(),
            id: BuiltValueNullFieldError.checkNotNull(id, r'TeamCreate', 'id'),
            memberIds: _memberIds?.build(),
            name: BuiltValueNullFieldError.checkNotNull(
                name, r'TeamCreate', 'name'),
            orgId: BuiltValueNullFieldError.checkNotNull(
                orgId, r'TeamCreate', 'orgId'),
          );
    } catch (_) {
      late String _$failedField;
      try {
        _$failedField = 'extraData';
        _extraData?.build();

        _$failedField = 'memberIds';
        _memberIds?.build();
      } catch (e) {
        throw BuiltValueNestedFieldError(
            r'TeamCreate', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
