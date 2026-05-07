// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'violation_info.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$ViolationInfo extends ViolationInfo {
  @override
  final String constraintKey;
  @override
  final BuiltList<String> entities;
  @override
  final String message;
  @override
  final String severity;

  factory _$ViolationInfo([void Function(ViolationInfoBuilder)? updates]) =>
      (ViolationInfoBuilder()..update(updates))._build();

  _$ViolationInfo._(
      {required this.constraintKey,
      required this.entities,
      required this.message,
      required this.severity})
      : super._();
  @override
  ViolationInfo rebuild(void Function(ViolationInfoBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  ViolationInfoBuilder toBuilder() => ViolationInfoBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is ViolationInfo &&
        constraintKey == other.constraintKey &&
        entities == other.entities &&
        message == other.message &&
        severity == other.severity;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, constraintKey.hashCode);
    _$hash = $jc(_$hash, entities.hashCode);
    _$hash = $jc(_$hash, message.hashCode);
    _$hash = $jc(_$hash, severity.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'ViolationInfo')
          ..add('constraintKey', constraintKey)
          ..add('entities', entities)
          ..add('message', message)
          ..add('severity', severity))
        .toString();
  }
}

class ViolationInfoBuilder
    implements Builder<ViolationInfo, ViolationInfoBuilder> {
  _$ViolationInfo? _$v;

  String? _constraintKey;
  String? get constraintKey => _$this._constraintKey;
  set constraintKey(String? constraintKey) =>
      _$this._constraintKey = constraintKey;

  ListBuilder<String>? _entities;
  ListBuilder<String> get entities =>
      _$this._entities ??= ListBuilder<String>();
  set entities(ListBuilder<String>? entities) => _$this._entities = entities;

  String? _message;
  String? get message => _$this._message;
  set message(String? message) => _$this._message = message;

  String? _severity;
  String? get severity => _$this._severity;
  set severity(String? severity) => _$this._severity = severity;

  ViolationInfoBuilder() {
    ViolationInfo._defaults(this);
  }

  ViolationInfoBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _constraintKey = $v.constraintKey;
      _entities = $v.entities.toBuilder();
      _message = $v.message;
      _severity = $v.severity;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(ViolationInfo other) {
    _$v = other as _$ViolationInfo;
  }

  @override
  void update(void Function(ViolationInfoBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  ViolationInfo build() => _build();

  _$ViolationInfo _build() {
    _$ViolationInfo _$result;
    try {
      _$result = _$v ??
          _$ViolationInfo._(
            constraintKey: BuiltValueNullFieldError.checkNotNull(
                constraintKey, r'ViolationInfo', 'constraintKey'),
            entities: entities.build(),
            message: BuiltValueNullFieldError.checkNotNull(
                message, r'ViolationInfo', 'message'),
            severity: BuiltValueNullFieldError.checkNotNull(
                severity, r'ViolationInfo', 'severity'),
          );
    } catch (_) {
      late String _$failedField;
      try {
        _$failedField = 'entities';
        entities.build();
      } catch (e) {
        throw BuiltValueNestedFieldError(
            r'ViolationInfo', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
