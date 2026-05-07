// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'resource_response.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$ResourceResponse extends ResourceResponse {
  @override
  final int? capacity;
  @override
  final DateTime createdAt;
  @override
  final BuiltMap<String, JsonObject?>? extraData;
  @override
  final String id;
  @override
  final String location;
  @override
  final String orgId;
  @override
  final String type;
  @override
  final DateTime updatedAt;

  factory _$ResourceResponse(
          [void Function(ResourceResponseBuilder)? updates]) =>
      (ResourceResponseBuilder()..update(updates))._build();

  _$ResourceResponse._(
      {this.capacity,
      required this.createdAt,
      this.extraData,
      required this.id,
      required this.location,
      required this.orgId,
      required this.type,
      required this.updatedAt})
      : super._();
  @override
  ResourceResponse rebuild(void Function(ResourceResponseBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  ResourceResponseBuilder toBuilder() =>
      ResourceResponseBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is ResourceResponse &&
        capacity == other.capacity &&
        createdAt == other.createdAt &&
        extraData == other.extraData &&
        id == other.id &&
        location == other.location &&
        orgId == other.orgId &&
        type == other.type &&
        updatedAt == other.updatedAt;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, capacity.hashCode);
    _$hash = $jc(_$hash, createdAt.hashCode);
    _$hash = $jc(_$hash, extraData.hashCode);
    _$hash = $jc(_$hash, id.hashCode);
    _$hash = $jc(_$hash, location.hashCode);
    _$hash = $jc(_$hash, orgId.hashCode);
    _$hash = $jc(_$hash, type.hashCode);
    _$hash = $jc(_$hash, updatedAt.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'ResourceResponse')
          ..add('capacity', capacity)
          ..add('createdAt', createdAt)
          ..add('extraData', extraData)
          ..add('id', id)
          ..add('location', location)
          ..add('orgId', orgId)
          ..add('type', type)
          ..add('updatedAt', updatedAt))
        .toString();
  }
}

class ResourceResponseBuilder
    implements Builder<ResourceResponse, ResourceResponseBuilder> {
  _$ResourceResponse? _$v;

  int? _capacity;
  int? get capacity => _$this._capacity;
  set capacity(int? capacity) => _$this._capacity = capacity;

  DateTime? _createdAt;
  DateTime? get createdAt => _$this._createdAt;
  set createdAt(DateTime? createdAt) => _$this._createdAt = createdAt;

  MapBuilder<String, JsonObject?>? _extraData;
  MapBuilder<String, JsonObject?> get extraData =>
      _$this._extraData ??= MapBuilder<String, JsonObject?>();
  set extraData(MapBuilder<String, JsonObject?>? extraData) =>
      _$this._extraData = extraData;

  String? _id;
  String? get id => _$this._id;
  set id(String? id) => _$this._id = id;

  String? _location;
  String? get location => _$this._location;
  set location(String? location) => _$this._location = location;

  String? _orgId;
  String? get orgId => _$this._orgId;
  set orgId(String? orgId) => _$this._orgId = orgId;

  String? _type;
  String? get type => _$this._type;
  set type(String? type) => _$this._type = type;

  DateTime? _updatedAt;
  DateTime? get updatedAt => _$this._updatedAt;
  set updatedAt(DateTime? updatedAt) => _$this._updatedAt = updatedAt;

  ResourceResponseBuilder() {
    ResourceResponse._defaults(this);
  }

  ResourceResponseBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _capacity = $v.capacity;
      _createdAt = $v.createdAt;
      _extraData = $v.extraData?.toBuilder();
      _id = $v.id;
      _location = $v.location;
      _orgId = $v.orgId;
      _type = $v.type;
      _updatedAt = $v.updatedAt;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(ResourceResponse other) {
    _$v = other as _$ResourceResponse;
  }

  @override
  void update(void Function(ResourceResponseBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  ResourceResponse build() => _build();

  _$ResourceResponse _build() {
    _$ResourceResponse _$result;
    try {
      _$result = _$v ??
          _$ResourceResponse._(
            capacity: capacity,
            createdAt: BuiltValueNullFieldError.checkNotNull(
                createdAt, r'ResourceResponse', 'createdAt'),
            extraData: _extraData?.build(),
            id: BuiltValueNullFieldError.checkNotNull(
                id, r'ResourceResponse', 'id'),
            location: BuiltValueNullFieldError.checkNotNull(
                location, r'ResourceResponse', 'location'),
            orgId: BuiltValueNullFieldError.checkNotNull(
                orgId, r'ResourceResponse', 'orgId'),
            type: BuiltValueNullFieldError.checkNotNull(
                type, r'ResourceResponse', 'type'),
            updatedAt: BuiltValueNullFieldError.checkNotNull(
                updatedAt, r'ResourceResponse', 'updatedAt'),
          );
    } catch (_) {
      late String _$failedField;
      try {
        _$failedField = 'extraData';
        _extraData?.build();
      } catch (e) {
        throw BuiltValueNestedFieldError(
            r'ResourceResponse', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
