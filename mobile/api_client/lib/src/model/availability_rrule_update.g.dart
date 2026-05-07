// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'availability_rrule_update.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$AvailabilityRruleUpdate extends AvailabilityRruleUpdate {
  @override
  final String rrule;

  factory _$AvailabilityRruleUpdate(
          [void Function(AvailabilityRruleUpdateBuilder)? updates]) =>
      (AvailabilityRruleUpdateBuilder()..update(updates))._build();

  _$AvailabilityRruleUpdate._({required this.rrule}) : super._();
  @override
  AvailabilityRruleUpdate rebuild(
          void Function(AvailabilityRruleUpdateBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  AvailabilityRruleUpdateBuilder toBuilder() =>
      AvailabilityRruleUpdateBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is AvailabilityRruleUpdate && rrule == other.rrule;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, rrule.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'AvailabilityRruleUpdate')
          ..add('rrule', rrule))
        .toString();
  }
}

class AvailabilityRruleUpdateBuilder
    implements
        Builder<AvailabilityRruleUpdate, AvailabilityRruleUpdateBuilder> {
  _$AvailabilityRruleUpdate? _$v;

  String? _rrule;
  String? get rrule => _$this._rrule;
  set rrule(String? rrule) => _$this._rrule = rrule;

  AvailabilityRruleUpdateBuilder() {
    AvailabilityRruleUpdate._defaults(this);
  }

  AvailabilityRruleUpdateBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _rrule = $v.rrule;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(AvailabilityRruleUpdate other) {
    _$v = other as _$AvailabilityRruleUpdate;
  }

  @override
  void update(void Function(AvailabilityRruleUpdateBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  AvailabilityRruleUpdate build() => _build();

  _$AvailabilityRruleUpdate _build() {
    final _$result = _$v ??
        _$AvailabilityRruleUpdate._(
          rrule: BuiltValueNullFieldError.checkNotNull(
              rrule, r'AvailabilityRruleUpdate', 'rrule'),
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
