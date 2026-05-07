// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'availability_exception_create.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$AvailabilityExceptionCreate extends AvailabilityExceptionCreate {
  @override
  final Date exceptionDate;

  factory _$AvailabilityExceptionCreate(
          [void Function(AvailabilityExceptionCreateBuilder)? updates]) =>
      (AvailabilityExceptionCreateBuilder()..update(updates))._build();

  _$AvailabilityExceptionCreate._({required this.exceptionDate}) : super._();
  @override
  AvailabilityExceptionCreate rebuild(
          void Function(AvailabilityExceptionCreateBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  AvailabilityExceptionCreateBuilder toBuilder() =>
      AvailabilityExceptionCreateBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is AvailabilityExceptionCreate &&
        exceptionDate == other.exceptionDate;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, exceptionDate.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'AvailabilityExceptionCreate')
          ..add('exceptionDate', exceptionDate))
        .toString();
  }
}

class AvailabilityExceptionCreateBuilder
    implements
        Builder<AvailabilityExceptionCreate,
            AvailabilityExceptionCreateBuilder> {
  _$AvailabilityExceptionCreate? _$v;

  Date? _exceptionDate;
  Date? get exceptionDate => _$this._exceptionDate;
  set exceptionDate(Date? exceptionDate) =>
      _$this._exceptionDate = exceptionDate;

  AvailabilityExceptionCreateBuilder() {
    AvailabilityExceptionCreate._defaults(this);
  }

  AvailabilityExceptionCreateBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _exceptionDate = $v.exceptionDate;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(AvailabilityExceptionCreate other) {
    _$v = other as _$AvailabilityExceptionCreate;
  }

  @override
  void update(void Function(AvailabilityExceptionCreateBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  AvailabilityExceptionCreate build() => _build();

  _$AvailabilityExceptionCreate _build() {
    final _$result = _$v ??
        _$AvailabilityExceptionCreate._(
          exceptionDate: BuiltValueNullFieldError.checkNotNull(
              exceptionDate, r'AvailabilityExceptionCreate', 'exceptionDate'),
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
