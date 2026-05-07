// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'team_update.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$TeamUpdate extends TeamUpdate {
  @override
  final String? description;
  @override
  final BuiltMap<String, JsonObject?>? extraData;
  @override
  final String? name;

  factory _$TeamUpdate([void Function(TeamUpdateBuilder)? updates]) =>
      (TeamUpdateBuilder()..update(updates))._build();

  _$TeamUpdate._({this.description, this.extraData, this.name}) : super._();
  @override
  TeamUpdate rebuild(void Function(TeamUpdateBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  TeamUpdateBuilder toBuilder() => TeamUpdateBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is TeamUpdate &&
        description == other.description &&
        extraData == other.extraData &&
        name == other.name;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, description.hashCode);
    _$hash = $jc(_$hash, extraData.hashCode);
    _$hash = $jc(_$hash, name.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'TeamUpdate')
          ..add('description', description)
          ..add('extraData', extraData)
          ..add('name', name))
        .toString();
  }
}

class TeamUpdateBuilder implements Builder<TeamUpdate, TeamUpdateBuilder> {
  _$TeamUpdate? _$v;

  String? _description;
  String? get description => _$this._description;
  set description(String? description) => _$this._description = description;

  MapBuilder<String, JsonObject?>? _extraData;
  MapBuilder<String, JsonObject?> get extraData =>
      _$this._extraData ??= MapBuilder<String, JsonObject?>();
  set extraData(MapBuilder<String, JsonObject?>? extraData) =>
      _$this._extraData = extraData;

  String? _name;
  String? get name => _$this._name;
  set name(String? name) => _$this._name = name;

  TeamUpdateBuilder() {
    TeamUpdate._defaults(this);
  }

  TeamUpdateBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _description = $v.description;
      _extraData = $v.extraData?.toBuilder();
      _name = $v.name;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(TeamUpdate other) {
    _$v = other as _$TeamUpdate;
  }

  @override
  void update(void Function(TeamUpdateBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  TeamUpdate build() => _build();

  _$TeamUpdate _build() {
    _$TeamUpdate _$result;
    try {
      _$result = _$v ??
          _$TeamUpdate._(
            description: description,
            extraData: _extraData?.build(),
            name: name,
          );
    } catch (_) {
      late String _$failedField;
      try {
        _$failedField = 'extraData';
        _extraData?.build();
      } catch (e) {
        throw BuiltValueNestedFieldError(
            r'TeamUpdate', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
