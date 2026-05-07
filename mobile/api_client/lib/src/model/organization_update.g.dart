// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'organization_update.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$OrganizationUpdate extends OrganizationUpdate {
  @override
  final BuiltMap<String, JsonObject?>? config;
  @override
  final String? name;
  @override
  final String? region;

  factory _$OrganizationUpdate(
          [void Function(OrganizationUpdateBuilder)? updates]) =>
      (OrganizationUpdateBuilder()..update(updates))._build();

  _$OrganizationUpdate._({this.config, this.name, this.region}) : super._();
  @override
  OrganizationUpdate rebuild(
          void Function(OrganizationUpdateBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  OrganizationUpdateBuilder toBuilder() =>
      OrganizationUpdateBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is OrganizationUpdate &&
        config == other.config &&
        name == other.name &&
        region == other.region;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, config.hashCode);
    _$hash = $jc(_$hash, name.hashCode);
    _$hash = $jc(_$hash, region.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'OrganizationUpdate')
          ..add('config', config)
          ..add('name', name)
          ..add('region', region))
        .toString();
  }
}

class OrganizationUpdateBuilder
    implements Builder<OrganizationUpdate, OrganizationUpdateBuilder> {
  _$OrganizationUpdate? _$v;

  MapBuilder<String, JsonObject?>? _config;
  MapBuilder<String, JsonObject?> get config =>
      _$this._config ??= MapBuilder<String, JsonObject?>();
  set config(MapBuilder<String, JsonObject?>? config) =>
      _$this._config = config;

  String? _name;
  String? get name => _$this._name;
  set name(String? name) => _$this._name = name;

  String? _region;
  String? get region => _$this._region;
  set region(String? region) => _$this._region = region;

  OrganizationUpdateBuilder() {
    OrganizationUpdate._defaults(this);
  }

  OrganizationUpdateBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _config = $v.config?.toBuilder();
      _name = $v.name;
      _region = $v.region;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(OrganizationUpdate other) {
    _$v = other as _$OrganizationUpdate;
  }

  @override
  void update(void Function(OrganizationUpdateBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  OrganizationUpdate build() => _build();

  _$OrganizationUpdate _build() {
    _$OrganizationUpdate _$result;
    try {
      _$result = _$v ??
          _$OrganizationUpdate._(
            config: _config?.build(),
            name: name,
            region: region,
          );
    } catch (_) {
      late String _$failedField;
      try {
        _$failedField = 'config';
        _config?.build();
      } catch (e) {
        throw BuiltValueNestedFieldError(
            r'OrganizationUpdate', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
