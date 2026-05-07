// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'availability_exception_response.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$AvailabilityExceptionResponse extends AvailabilityExceptionResponse {
  @override
  final Date exceptionDate;
  @override
  final int id;

  factory _$AvailabilityExceptionResponse(
          [void Function(AvailabilityExceptionResponseBuilder)? updates]) =>
      (AvailabilityExceptionResponseBuilder()..update(updates))._build();

  _$AvailabilityExceptionResponse._(
      {required this.exceptionDate, required this.id})
      : super._();
  @override
  AvailabilityExceptionResponse rebuild(
          void Function(AvailabilityExceptionResponseBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  AvailabilityExceptionResponseBuilder toBuilder() =>
      AvailabilityExceptionResponseBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is AvailabilityExceptionResponse &&
        exceptionDate == other.exceptionDate &&
        id == other.id;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, exceptionDate.hashCode);
    _$hash = $jc(_$hash, id.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'AvailabilityExceptionResponse')
          ..add('exceptionDate', exceptionDate)
          ..add('id', id))
        .toString();
  }
}

class AvailabilityExceptionResponseBuilder
    implements
        Builder<AvailabilityExceptionResponse,
            AvailabilityExceptionResponseBuilder> {
  _$AvailabilityExceptionResponse? _$v;

  Date? _exceptionDate;
  Date? get exceptionDate => _$this._exceptionDate;
  set exceptionDate(Date? exceptionDate) =>
      _$this._exceptionDate = exceptionDate;

  int? _id;
  int? get id => _$this._id;
  set id(int? id) => _$this._id = id;

  AvailabilityExceptionResponseBuilder() {
    AvailabilityExceptionResponse._defaults(this);
  }

  AvailabilityExceptionResponseBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _exceptionDate = $v.exceptionDate;
      _id = $v.id;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(AvailabilityExceptionResponse other) {
    _$v = other as _$AvailabilityExceptionResponse;
  }

  @override
  void update(void Function(AvailabilityExceptionResponseBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  AvailabilityExceptionResponse build() => _build();

  _$AvailabilityExceptionResponse _build() {
    final _$result = _$v ??
        _$AvailabilityExceptionResponse._(
          exceptionDate: BuiltValueNullFieldError.checkNotNull(
              exceptionDate, r'AvailabilityExceptionResponse', 'exceptionDate'),
          id: BuiltValueNullFieldError.checkNotNull(
              id, r'AvailabilityExceptionResponse', 'id'),
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
