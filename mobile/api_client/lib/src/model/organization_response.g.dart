// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'organization_response.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$OrganizationResponse extends OrganizationResponse {
  @override
  final DateTime? cancelledAt;
  @override
  final BuiltMap<String, JsonObject?>? config;
  @override
  final DateTime createdAt;
  @override
  final DateTime? dataRetentionUntil;
  @override
  final DateTime? deletionScheduledAt;
  @override
  final String id;
  @override
  final String name;
  @override
  final String? region;
  @override
  final DateTime updatedAt;

  factory _$OrganizationResponse(
          [void Function(OrganizationResponseBuilder)? updates]) =>
      (OrganizationResponseBuilder()..update(updates))._build();

  _$OrganizationResponse._(
      {this.cancelledAt,
      this.config,
      required this.createdAt,
      this.dataRetentionUntil,
      this.deletionScheduledAt,
      required this.id,
      required this.name,
      this.region,
      required this.updatedAt})
      : super._();
  @override
  OrganizationResponse rebuild(
          void Function(OrganizationResponseBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  OrganizationResponseBuilder toBuilder() =>
      OrganizationResponseBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is OrganizationResponse &&
        cancelledAt == other.cancelledAt &&
        config == other.config &&
        createdAt == other.createdAt &&
        dataRetentionUntil == other.dataRetentionUntil &&
        deletionScheduledAt == other.deletionScheduledAt &&
        id == other.id &&
        name == other.name &&
        region == other.region &&
        updatedAt == other.updatedAt;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, cancelledAt.hashCode);
    _$hash = $jc(_$hash, config.hashCode);
    _$hash = $jc(_$hash, createdAt.hashCode);
    _$hash = $jc(_$hash, dataRetentionUntil.hashCode);
    _$hash = $jc(_$hash, deletionScheduledAt.hashCode);
    _$hash = $jc(_$hash, id.hashCode);
    _$hash = $jc(_$hash, name.hashCode);
    _$hash = $jc(_$hash, region.hashCode);
    _$hash = $jc(_$hash, updatedAt.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'OrganizationResponse')
          ..add('cancelledAt', cancelledAt)
          ..add('config', config)
          ..add('createdAt', createdAt)
          ..add('dataRetentionUntil', dataRetentionUntil)
          ..add('deletionScheduledAt', deletionScheduledAt)
          ..add('id', id)
          ..add('name', name)
          ..add('region', region)
          ..add('updatedAt', updatedAt))
        .toString();
  }
}

class OrganizationResponseBuilder
    implements Builder<OrganizationResponse, OrganizationResponseBuilder> {
  _$OrganizationResponse? _$v;

  DateTime? _cancelledAt;
  DateTime? get cancelledAt => _$this._cancelledAt;
  set cancelledAt(DateTime? cancelledAt) => _$this._cancelledAt = cancelledAt;

  MapBuilder<String, JsonObject?>? _config;
  MapBuilder<String, JsonObject?> get config =>
      _$this._config ??= MapBuilder<String, JsonObject?>();
  set config(MapBuilder<String, JsonObject?>? config) =>
      _$this._config = config;

  DateTime? _createdAt;
  DateTime? get createdAt => _$this._createdAt;
  set createdAt(DateTime? createdAt) => _$this._createdAt = createdAt;

  DateTime? _dataRetentionUntil;
  DateTime? get dataRetentionUntil => _$this._dataRetentionUntil;
  set dataRetentionUntil(DateTime? dataRetentionUntil) =>
      _$this._dataRetentionUntil = dataRetentionUntil;

  DateTime? _deletionScheduledAt;
  DateTime? get deletionScheduledAt => _$this._deletionScheduledAt;
  set deletionScheduledAt(DateTime? deletionScheduledAt) =>
      _$this._deletionScheduledAt = deletionScheduledAt;

  String? _id;
  String? get id => _$this._id;
  set id(String? id) => _$this._id = id;

  String? _name;
  String? get name => _$this._name;
  set name(String? name) => _$this._name = name;

  String? _region;
  String? get region => _$this._region;
  set region(String? region) => _$this._region = region;

  DateTime? _updatedAt;
  DateTime? get updatedAt => _$this._updatedAt;
  set updatedAt(DateTime? updatedAt) => _$this._updatedAt = updatedAt;

  OrganizationResponseBuilder() {
    OrganizationResponse._defaults(this);
  }

  OrganizationResponseBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _cancelledAt = $v.cancelledAt;
      _config = $v.config?.toBuilder();
      _createdAt = $v.createdAt;
      _dataRetentionUntil = $v.dataRetentionUntil;
      _deletionScheduledAt = $v.deletionScheduledAt;
      _id = $v.id;
      _name = $v.name;
      _region = $v.region;
      _updatedAt = $v.updatedAt;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(OrganizationResponse other) {
    _$v = other as _$OrganizationResponse;
  }

  @override
  void update(void Function(OrganizationResponseBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  OrganizationResponse build() => _build();

  _$OrganizationResponse _build() {
    _$OrganizationResponse _$result;
    try {
      _$result = _$v ??
          _$OrganizationResponse._(
            cancelledAt: cancelledAt,
            config: _config?.build(),
            createdAt: BuiltValueNullFieldError.checkNotNull(
                createdAt, r'OrganizationResponse', 'createdAt'),
            dataRetentionUntil: dataRetentionUntil,
            deletionScheduledAt: deletionScheduledAt,
            id: BuiltValueNullFieldError.checkNotNull(
                id, r'OrganizationResponse', 'id'),
            name: BuiltValueNullFieldError.checkNotNull(
                name, r'OrganizationResponse', 'name'),
            region: region,
            updatedAt: BuiltValueNullFieldError.checkNotNull(
                updatedAt, r'OrganizationResponse', 'updatedAt'),
          );
    } catch (_) {
      late String _$failedField;
      try {
        _$failedField = 'config';
        _config?.build();
      } catch (e) {
        throw BuiltValueNestedFieldError(
            r'OrganizationResponse', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
