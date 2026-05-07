// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'constraint_update.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$ConstraintUpdate extends ConstraintUpdate {
  @override
  final BuiltMap<String, JsonObject?>? params;
  @override
  final String? predicate;
  @override
  final String? type;
  @override
  final int? weight;

  factory _$ConstraintUpdate(
          [void Function(ConstraintUpdateBuilder)? updates]) =>
      (ConstraintUpdateBuilder()..update(updates))._build();

  _$ConstraintUpdate._({this.params, this.predicate, this.type, this.weight})
      : super._();
  @override
  ConstraintUpdate rebuild(void Function(ConstraintUpdateBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  ConstraintUpdateBuilder toBuilder() =>
      ConstraintUpdateBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is ConstraintUpdate &&
        params == other.params &&
        predicate == other.predicate &&
        type == other.type &&
        weight == other.weight;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, params.hashCode);
    _$hash = $jc(_$hash, predicate.hashCode);
    _$hash = $jc(_$hash, type.hashCode);
    _$hash = $jc(_$hash, weight.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'ConstraintUpdate')
          ..add('params', params)
          ..add('predicate', predicate)
          ..add('type', type)
          ..add('weight', weight))
        .toString();
  }
}

class ConstraintUpdateBuilder
    implements Builder<ConstraintUpdate, ConstraintUpdateBuilder> {
  _$ConstraintUpdate? _$v;

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

  ConstraintUpdateBuilder() {
    ConstraintUpdate._defaults(this);
  }

  ConstraintUpdateBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _params = $v.params?.toBuilder();
      _predicate = $v.predicate;
      _type = $v.type;
      _weight = $v.weight;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(ConstraintUpdate other) {
    _$v = other as _$ConstraintUpdate;
  }

  @override
  void update(void Function(ConstraintUpdateBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  ConstraintUpdate build() => _build();

  _$ConstraintUpdate _build() {
    _$ConstraintUpdate _$result;
    try {
      _$result = _$v ??
          _$ConstraintUpdate._(
            params: _params?.build(),
            predicate: predicate,
            type: type,
            weight: weight,
          );
    } catch (_) {
      late String _$failedField;
      try {
        _$failedField = 'params';
        _params?.build();
      } catch (e) {
        throw BuiltValueNestedFieldError(
            r'ConstraintUpdate', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
