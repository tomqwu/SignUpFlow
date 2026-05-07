// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'team_response.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$TeamResponse extends TeamResponse {
  @override
  final DateTime createdAt;
  @override
  final String? description;
  @override
  final BuiltMap<String, JsonObject?>? extraData;
  @override
  final String id;
  @override
  final int? memberCount;
  @override
  final String name;
  @override
  final String orgId;
  @override
  final DateTime updatedAt;

  factory _$TeamResponse([void Function(TeamResponseBuilder)? updates]) =>
      (TeamResponseBuilder()..update(updates))._build();

  _$TeamResponse._(
      {required this.createdAt,
      this.description,
      this.extraData,
      required this.id,
      this.memberCount,
      required this.name,
      required this.orgId,
      required this.updatedAt})
      : super._();
  @override
  TeamResponse rebuild(void Function(TeamResponseBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  TeamResponseBuilder toBuilder() => TeamResponseBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is TeamResponse &&
        createdAt == other.createdAt &&
        description == other.description &&
        extraData == other.extraData &&
        id == other.id &&
        memberCount == other.memberCount &&
        name == other.name &&
        orgId == other.orgId &&
        updatedAt == other.updatedAt;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, createdAt.hashCode);
    _$hash = $jc(_$hash, description.hashCode);
    _$hash = $jc(_$hash, extraData.hashCode);
    _$hash = $jc(_$hash, id.hashCode);
    _$hash = $jc(_$hash, memberCount.hashCode);
    _$hash = $jc(_$hash, name.hashCode);
    _$hash = $jc(_$hash, orgId.hashCode);
    _$hash = $jc(_$hash, updatedAt.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'TeamResponse')
          ..add('createdAt', createdAt)
          ..add('description', description)
          ..add('extraData', extraData)
          ..add('id', id)
          ..add('memberCount', memberCount)
          ..add('name', name)
          ..add('orgId', orgId)
          ..add('updatedAt', updatedAt))
        .toString();
  }
}

class TeamResponseBuilder
    implements Builder<TeamResponse, TeamResponseBuilder> {
  _$TeamResponse? _$v;

  DateTime? _createdAt;
  DateTime? get createdAt => _$this._createdAt;
  set createdAt(DateTime? createdAt) => _$this._createdAt = createdAt;

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

  int? _memberCount;
  int? get memberCount => _$this._memberCount;
  set memberCount(int? memberCount) => _$this._memberCount = memberCount;

  String? _name;
  String? get name => _$this._name;
  set name(String? name) => _$this._name = name;

  String? _orgId;
  String? get orgId => _$this._orgId;
  set orgId(String? orgId) => _$this._orgId = orgId;

  DateTime? _updatedAt;
  DateTime? get updatedAt => _$this._updatedAt;
  set updatedAt(DateTime? updatedAt) => _$this._updatedAt = updatedAt;

  TeamResponseBuilder() {
    TeamResponse._defaults(this);
  }

  TeamResponseBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _createdAt = $v.createdAt;
      _description = $v.description;
      _extraData = $v.extraData?.toBuilder();
      _id = $v.id;
      _memberCount = $v.memberCount;
      _name = $v.name;
      _orgId = $v.orgId;
      _updatedAt = $v.updatedAt;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(TeamResponse other) {
    _$v = other as _$TeamResponse;
  }

  @override
  void update(void Function(TeamResponseBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  TeamResponse build() => _build();

  _$TeamResponse _build() {
    _$TeamResponse _$result;
    try {
      _$result = _$v ??
          _$TeamResponse._(
            createdAt: BuiltValueNullFieldError.checkNotNull(
                createdAt, r'TeamResponse', 'createdAt'),
            description: description,
            extraData: _extraData?.build(),
            id: BuiltValueNullFieldError.checkNotNull(
                id, r'TeamResponse', 'id'),
            memberCount: memberCount,
            name: BuiltValueNullFieldError.checkNotNull(
                name, r'TeamResponse', 'name'),
            orgId: BuiltValueNullFieldError.checkNotNull(
                orgId, r'TeamResponse', 'orgId'),
            updatedAt: BuiltValueNullFieldError.checkNotNull(
                updatedAt, r'TeamResponse', 'updatedAt'),
          );
    } catch (_) {
      late String _$failedField;
      try {
        _$failedField = 'extraData';
        _extraData?.build();
      } catch (e) {
        throw BuiltValueNestedFieldError(
            r'TeamResponse', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
