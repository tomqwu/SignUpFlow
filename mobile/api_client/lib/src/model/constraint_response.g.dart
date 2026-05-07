// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'constraint_response.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$ConstraintResponse extends ConstraintResponse {
  @override
  final DateTime createdAt;
  @override
  final int id;
  @override
  final String key;
  @override
  final String orgId;
  @override
  final BuiltMap<String, JsonObject?>? params;
  @override
  final String predicate;
  @override
  final String type;
  @override
  final DateTime updatedAt;
  @override
  final int? weight;

  factory _$ConstraintResponse(
          [void Function(ConstraintResponseBuilder)? updates]) =>
      (ConstraintResponseBuilder()..update(updates))._build();

  _$ConstraintResponse._(
      {required this.createdAt,
      required this.id,
      required this.key,
      required this.orgId,
      this.params,
      required this.predicate,
      required this.type,
      required this.updatedAt,
      this.weight})
      : super._();
  @override
  ConstraintResponse rebuild(
          void Function(ConstraintResponseBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  ConstraintResponseBuilder toBuilder() =>
      ConstraintResponseBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is ConstraintResponse &&
        createdAt == other.createdAt &&
        id == other.id &&
        key == other.key &&
        orgId == other.orgId &&
        params == other.params &&
        predicate == other.predicate &&
        type == other.type &&
        updatedAt == other.updatedAt &&
        weight == other.weight;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, createdAt.hashCode);
    _$hash = $jc(_$hash, id.hashCode);
    _$hash = $jc(_$hash, key.hashCode);
    _$hash = $jc(_$hash, orgId.hashCode);
    _$hash = $jc(_$hash, params.hashCode);
    _$hash = $jc(_$hash, predicate.hashCode);
    _$hash = $jc(_$hash, type.hashCode);
    _$hash = $jc(_$hash, updatedAt.hashCode);
    _$hash = $jc(_$hash, weight.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'ConstraintResponse')
          ..add('createdAt', createdAt)
          ..add('id', id)
          ..add('key', key)
          ..add('orgId', orgId)
          ..add('params', params)
          ..add('predicate', predicate)
          ..add('type', type)
          ..add('updatedAt', updatedAt)
          ..add('weight', weight))
        .toString();
  }
}

class ConstraintResponseBuilder
    implements Builder<ConstraintResponse, ConstraintResponseBuilder> {
  _$ConstraintResponse? _$v;

  DateTime? _createdAt;
  DateTime? get createdAt => _$this._createdAt;
  set createdAt(DateTime? createdAt) => _$this._createdAt = createdAt;

  int? _id;
  int? get id => _$this._id;
  set id(int? id) => _$this._id = id;

  String? _key;
  String? get key => _$this._key;
  set key(String? key) => _$this._key = key;

  String? _orgId;
  String? get orgId => _$this._orgId;
  set orgId(String? orgId) => _$this._orgId = orgId;

  MapBuilder<String, JsonObject?>? _params;
  MapBuilder<String, JsonObject?> get params =>
      _$this._params ??= MapBuilder<String, JsonObject?>();
  set params(MapBuilder<String, JsonObject?>? params) =>
      _$this._params = params;

  String? _predicate;
  String? get predicate => _$this._predicate;
  set predicate(String? predicate) => _$this._predicate = predicate;

  String? _type;
  String? get type => _$this._type;
  set type(String? type) => _$this._type = type;

  DateTime? _updatedAt;
  DateTime? get updatedAt => _$this._updatedAt;
  set updatedAt(DateTime? updatedAt) => _$this._updatedAt = updatedAt;

  int? _weight;
  int? get weight => _$this._weight;
  set weight(int? weight) => _$this._weight = weight;

  ConstraintResponseBuilder() {
    ConstraintResponse._defaults(this);
  }

  ConstraintResponseBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _createdAt = $v.createdAt;
      _id = $v.id;
      _key = $v.key;
      _orgId = $v.orgId;
      _params = $v.params?.toBuilder();
      _predicate = $v.predicate;
      _type = $v.type;
      _updatedAt = $v.updatedAt;
      _weight = $v.weight;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(ConstraintResponse other) {
    _$v = other as _$ConstraintResponse;
  }

  @override
  void update(void Function(ConstraintResponseBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  ConstraintResponse build() => _build();

  _$ConstraintResponse _build() {
    _$ConstraintResponse _$result;
    try {
      _$result = _$v ??
          _$ConstraintResponse._(
            createdAt: BuiltValueNullFieldError.checkNotNull(
                createdAt, r'ConstraintResponse', 'createdAt'),
            id: BuiltValueNullFieldError.checkNotNull(
                id, r'ConstraintResponse', 'id'),
            key: BuiltValueNullFieldError.checkNotNull(
                key, r'ConstraintResponse', 'key'),
            orgId: BuiltValueNullFieldError.checkNotNull(
                orgId, r'ConstraintResponse', 'orgId'),
            params: _params?.build(),
            predicate: BuiltValueNullFieldError.checkNotNull(
                predicate, r'ConstraintResponse', 'predicate'),
            type: BuiltValueNullFieldError.checkNotNull(
                type, r'ConstraintResponse', 'type'),
            updatedAt: BuiltValueNullFieldError.checkNotNull(
                updatedAt, r'ConstraintResponse', 'updatedAt'),
            weight: weight,
          );
    } catch (_) {
      late String _$failedField;
      try {
        _$failedField = 'params';
        _params?.build();
      } catch (e) {
        throw BuiltValueNestedFieldError(
            r'ConstraintResponse', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
