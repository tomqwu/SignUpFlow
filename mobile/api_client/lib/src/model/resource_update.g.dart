// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'resource_update.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$ResourceUpdate extends ResourceUpdate {
  @override
  final int? capacity;
  @override
  final BuiltMap<String, JsonObject?>? extraData;
  @override
  final String? location;
  @override
  final String? type;

  factory _$ResourceUpdate([void Function(ResourceUpdateBuilder)? updates]) =>
      (ResourceUpdateBuilder()..update(updates))._build();

  _$ResourceUpdate._({this.capacity, this.extraData, this.location, this.type})
      : super._();
  @override
  ResourceUpdate rebuild(void Function(ResourceUpdateBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  ResourceUpdateBuilder toBuilder() => ResourceUpdateBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is ResourceUpdate &&
        capacity == other.capacity &&
        extraData == other.extraData &&
        location == other.location &&
        type == other.type;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, capacity.hashCode);
    _$hash = $jc(_$hash, extraData.hashCode);
    _$hash = $jc(_$hash, location.hashCode);
    _$hash = $jc(_$hash, type.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'ResourceUpdate')
          ..add('capacity', capacity)
          ..add('extraData', extraData)
          ..add('location', location)
          ..add('type', type))
        .toString();
  }
}

class ResourceUpdateBuilder
    implements Builder<ResourceUpdate, ResourceUpdateBuilder> {
  _$ResourceUpdate? _$v;

  int? _capacity;
  int? get capacity => _$this._capacity;
  set capacity(int? capacity) => _$this._capacity = capacity;

  MapBuilder<String, JsonObject?>? _extraData;
  MapBuilder<String, JsonObject?> get extraData =>
      _$this._extraData ??= MapBuilder<String, JsonObject?>();
  set extraData(MapBuilder<String, JsonObject?>? extraData) =>
      _$this._extraData = extraData;

  String? _location;
  String? get location => _$this._location;
  set location(String? location) => _$this._location = location;

  String? _type;
  String? get type => _$this._type;
  set type(String? type) => _$this._type = type;

  ResourceUpdateBuilder() {
    ResourceUpdate._defaults(this);
  }

  ResourceUpdateBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _capacity = $v.capacity;
      _extraData = $v.extraData?.toBuilder();
      _location = $v.location;
      _type = $v.type;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(ResourceUpdate other) {
    _$v = other as _$ResourceUpdate;
  }

  @override
  void update(void Function(ResourceUpdateBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  ResourceUpdate build() => _build();

  _$ResourceUpdate _build() {
    _$ResourceUpdate _$result;
    try {
      _$result = _$v ??
          _$ResourceUpdate._(
            capacity: capacity,
            extraData: _extraData?.build(),
            location: location,
            type: type,
          );
    } catch (_) {
      late String _$failedField;
      try {
        _$failedField = 'extraData';
        _extraData?.build();
      } catch (e) {
        throw BuiltValueNestedFieldError(
            r'ResourceUpdate', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
