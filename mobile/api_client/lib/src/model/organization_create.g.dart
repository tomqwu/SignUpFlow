// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'organization_create.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$OrganizationCreate extends OrganizationCreate {
  @override
  final BuiltMap<String, JsonObject?>? config;
  @override
  final String id;
  @override
  final String name;
  @override
  final String? region;

  factory _$OrganizationCreate(
          [void Function(OrganizationCreateBuilder)? updates]) =>
      (OrganizationCreateBuilder()..update(updates))._build();

  _$OrganizationCreate._(
      {this.config, required this.id, required this.name, this.region})
      : super._();
  @override
  OrganizationCreate rebuild(
          void Function(OrganizationCreateBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  OrganizationCreateBuilder toBuilder() =>
      OrganizationCreateBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is OrganizationCreate &&
        config == other.config &&
        id == other.id &&
        name == other.name &&
        region == other.region;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, config.hashCode);
    _$hash = $jc(_$hash, id.hashCode);
    _$hash = $jc(_$hash, name.hashCode);
    _$hash = $jc(_$hash, region.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'OrganizationCreate')
          ..add('config', config)
          ..add('id', id)
          ..add('name', name)
          ..add('region', region))
        .toString();
  }
}

class OrganizationCreateBuilder
    implements Builder<OrganizationCreate, OrganizationCreateBuilder> {
  _$OrganizationCreate? _$v;

  MapBuilder<String, JsonObject?>? _config;
  MapBuilder<String, JsonObject?> get config =>
      _$this._config ??= MapBuilder<String, JsonObject?>();
  set config(MapBuilder<String, JsonObject?>? config) =>
      _$this._config = config;

  String? _id;
  String? get id => _$this._id;
  set id(String? id) => _$this._id = id;

  String? _name;
  String? get name => _$this._name;
  set name(String? name) => _$this._name = name;

  String? _region;
  String? get region => _$this._region;
  set region(String? region) => _$this._region = region;

  OrganizationCreateBuilder() {
    OrganizationCreate._defaults(this);
  }

  OrganizationCreateBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _config = $v.config?.toBuilder();
      _id = $v.id;
      _name = $v.name;
      _region = $v.region;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(OrganizationCreate other) {
    _$v = other as _$OrganizationCreate;
  }

  @override
  void update(void Function(OrganizationCreateBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  OrganizationCreate build() => _build();

  _$OrganizationCreate _build() {
    _$OrganizationCreate _$result;
    try {
      _$result = _$v ??
          _$OrganizationCreate._(
            config: _config?.build(),
            id: BuiltValueNullFieldError.checkNotNull(
                id, r'OrganizationCreate', 'id'),
            name: BuiltValueNullFieldError.checkNotNull(
                name, r'OrganizationCreate', 'name'),
            region: region,
          );
    } catch (_) {
      late String _$failedField;
      try {
        _$failedField = 'config';
        _config?.build();
      } catch (e) {
        throw BuiltValueNestedFieldError(
            r'OrganizationCreate', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
