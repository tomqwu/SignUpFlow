// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'availability_rrule_response.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$AvailabilityRruleResponse extends AvailabilityRruleResponse {
  @override
  final String? rrule;

  factory _$AvailabilityRruleResponse(
          [void Function(AvailabilityRruleResponseBuilder)? updates]) =>
      (AvailabilityRruleResponseBuilder()..update(updates))._build();

  _$AvailabilityRruleResponse._({this.rrule}) : super._();
  @override
  AvailabilityRruleResponse rebuild(
          void Function(AvailabilityRruleResponseBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  AvailabilityRruleResponseBuilder toBuilder() =>
      AvailabilityRruleResponseBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is AvailabilityRruleResponse && rrule == other.rrule;
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
    return (newBuiltValueToStringHelper(r'AvailabilityRruleResponse')
          ..add('rrule', rrule))
        .toString();
  }
}

class AvailabilityRruleResponseBuilder
    implements
        Builder<AvailabilityRruleResponse, AvailabilityRruleResponseBuilder> {
  _$AvailabilityRruleResponse? _$v;

  String? _rrule;
  String? get rrule => _$this._rrule;
  set rrule(String? rrule) => _$this._rrule = rrule;

  AvailabilityRruleResponseBuilder() {
    AvailabilityRruleResponse._defaults(this);
  }

  AvailabilityRruleResponseBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _rrule = $v.rrule;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(AvailabilityRruleResponse other) {
    _$v = other as _$AvailabilityRruleResponse;
  }

  @override
  void update(void Function(AvailabilityRruleResponseBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  AvailabilityRruleResponse build() => _build();

  _$AvailabilityRruleResponse _build() {
    final _$result = _$v ??
        _$AvailabilityRruleResponse._(
          rrule: rrule,
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
