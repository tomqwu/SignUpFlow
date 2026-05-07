// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'constraint_create.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$ConstraintCreate extends ConstraintCreate {
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
  final int? weight;

  factory _$ConstraintCreate(
          [void Function(ConstraintCreateBuilder)? updates]) =>
      (ConstraintCreateBuilder()..update(updates))._build();

  _$ConstraintCreate._(
      {required this.key,
      required this.orgId,
      this.params,
      required this.predicate,
      required this.type,
      this.weight})
      : super._();
  @override
  ConstraintCreate rebuild(void Function(ConstraintCreateBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  ConstraintCreateBuilder toBuilder() =>
      ConstraintCreateBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is ConstraintCreate &&
        key == other.key &&
        orgId == other.orgId &&
        params == other.params &&
        predicate == other.predicate &&
        type == other.type &&
        weight == other.weight;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, key.hashCode);
    _$hash = $jc(_$hash, orgId.hashCode);
    _$hash = $jc(_$hash, params.hashCode);
    _$hash = $jc(_$hash, predicate.hashCode);
    _$hash = $jc(_$hash, type.hashCode);
    _$hash = $jc(_$hash, weight.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'ConstraintCreate')
          ..add('key', key)
          ..add('orgId', orgId)
          ..add('params', params)
          ..add('predicate', predicate)
          ..add('type', type)
          ..add('weight', weight))
        .toString();
  }
}

class ConstraintCreateBuilder
    implements Builder<ConstraintCreate, ConstraintCreateBuilder> {
  _$ConstraintCreate? _$v;

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

  int? _weight;
  int? get weight => _$this._weight;
  set weight(int? weight) => _$this._weight = weight;

  ConstraintCreateBuilder() {
    ConstraintCreate._defaults(this);
  }

  ConstraintCreateBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _key = $v.key;
      _orgId = $v.orgId;
      _params = $v.params?.toBuilder();
      _predicate = $v.predicate;
      _type = $v.type;
      _weight = $v.weight;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(ConstraintCreate other) {
    _$v = other as _$ConstraintCreate;
  }

  @override
  void update(void Function(ConstraintCreateBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  ConstraintCreate build() => _build();

  _$ConstraintCreate _build() {
    _$ConstraintCreate _$result;
    try {
      _$result = _$v ??
          _$ConstraintCreate._(
            key: BuiltValueNullFieldError.checkNotNull(
                key, r'ConstraintCreate', 'key'),
            orgId: BuiltValueNullFieldError.checkNotNull(
                orgId, r'ConstraintCreate', 'orgId'),
            params: _params?.build(),
            predicate: BuiltValueNullFieldError.checkNotNull(
                predicate, r'ConstraintCreate', 'predicate'),
            type: BuiltValueNullFieldError.checkNotNull(
                type, r'ConstraintCreate', 'type'),
            weight: weight,
          );
    } catch (_) {
      late String _$failedField;
      try {
        _$failedField = 'params';
        _params?.build();
      } catch (e) {
        throw BuiltValueNestedFieldError(
            r'ConstraintCreate', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
