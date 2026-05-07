// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'resource_create.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$ResourceCreate extends ResourceCreate {
  @override
  final int? capacity;
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

  factory _$ResourceCreate([void Function(ResourceCreateBuilder)? updates]) =>
      (ResourceCreateBuilder()..update(updates))._build();

  _$ResourceCreate._(
      {this.capacity,
      this.extraData,
      required this.id,
      required this.location,
      required this.orgId,
      required this.type})
      : super._();
  @override
  ResourceCreate rebuild(void Function(ResourceCreateBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  ResourceCreateBuilder toBuilder() => ResourceCreateBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is ResourceCreate &&
        capacity == other.capacity &&
        extraData == other.extraData &&
        id == other.id &&
        location == other.location &&
        orgId == other.orgId &&
        type == other.type;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, capacity.hashCode);
    _$hash = $jc(_$hash, extraData.hashCode);
    _$hash = $jc(_$hash, id.hashCode);
    _$hash = $jc(_$hash, location.hashCode);
    _$hash = $jc(_$hash, orgId.hashCode);
    _$hash = $jc(_$hash, type.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'ResourceCreate')
          ..add('capacity', capacity)
          ..add('extraData', extraData)
          ..add('id', id)
          ..add('location', location)
          ..add('orgId', orgId)
          ..add('type', type))
        .toString();
  }
}

class ResourceCreateBuilder
    implements Builder<ResourceCreate, ResourceCreateBuilder> {
  _$ResourceCreate? _$v;

  int? _capacity;
  int? get capacity => _$this._capacity;
  set capacity(int? capacity) => _$this._capacity = capacity;

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

  ResourceCreateBuilder() {
    ResourceCreate._defaults(this);
  }

  ResourceCreateBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _capacity = $v.capacity;
      _extraData = $v.extraData?.toBuilder();
      _id = $v.id;
      _location = $v.location;
      _orgId = $v.orgId;
      _type = $v.type;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(ResourceCreate other) {
    _$v = other as _$ResourceCreate;
  }

  @override
  void update(void Function(ResourceCreateBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  ResourceCreate build() => _build();

  _$ResourceCreate _build() {
    _$ResourceCreate _$result;
    try {
      _$result = _$v ??
          _$ResourceCreate._(
            capacity: capacity,
            extraData: _extraData?.build(),
            id: BuiltValueNullFieldError.checkNotNull(
                id, r'ResourceCreate', 'id'),
            location: BuiltValueNullFieldError.checkNotNull(
                location, r'ResourceCreate', 'location'),
            orgId: BuiltValueNullFieldError.checkNotNull(
                orgId, r'ResourceCreate', 'orgId'),
            type: BuiltValueNullFieldError.checkNotNull(
                type, r'ResourceCreate', 'type'),
          );
    } catch (_) {
      late String _$failedField;
      try {
        _$failedField = 'extraData';
        _extraData?.build();
      } catch (e) {
        throw BuiltValueNestedFieldError(
            r'ResourceCreate', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
