// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'time_off_create.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$TimeOffCreate extends TimeOffCreate {
  @override
  final Date endDate;
  @override
  final String? reason;
  @override
  final Date startDate;

  factory _$TimeOffCreate([void Function(TimeOffCreateBuilder)? updates]) =>
      (TimeOffCreateBuilder()..update(updates))._build();

  _$TimeOffCreate._(
      {required this.endDate, this.reason, required this.startDate})
      : super._();
  @override
  TimeOffCreate rebuild(void Function(TimeOffCreateBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  TimeOffCreateBuilder toBuilder() => TimeOffCreateBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is TimeOffCreate &&
        endDate == other.endDate &&
        reason == other.reason &&
        startDate == other.startDate;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, endDate.hashCode);
    _$hash = $jc(_$hash, reason.hashCode);
    _$hash = $jc(_$hash, startDate.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'TimeOffCreate')
          ..add('endDate', endDate)
          ..add('reason', reason)
          ..add('startDate', startDate))
        .toString();
  }
}

class TimeOffCreateBuilder
    implements Builder<TimeOffCreate, TimeOffCreateBuilder> {
  _$TimeOffCreate? _$v;

  Date? _endDate;
  Date? get endDate => _$this._endDate;
  set endDate(Date? endDate) => _$this._endDate = endDate;

  String? _reason;
  String? get reason => _$this._reason;
  set reason(String? reason) => _$this._reason = reason;

  Date? _startDate;
  Date? get startDate => _$this._startDate;
  set startDate(Date? startDate) => _$this._startDate = startDate;

  TimeOffCreateBuilder() {
    TimeOffCreate._defaults(this);
  }

  TimeOffCreateBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _endDate = $v.endDate;
      _reason = $v.reason;
      _startDate = $v.startDate;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(TimeOffCreate other) {
    _$v = other as _$TimeOffCreate;
  }

  @override
  void update(void Function(TimeOffCreateBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  TimeOffCreate build() => _build();

  _$TimeOffCreate _build() {
    final _$result = _$v ??
        _$TimeOffCreate._(
          endDate: BuiltValueNullFieldError.checkNotNull(
              endDate, r'TimeOffCreate', 'endDate'),
          reason: reason,
          startDate: BuiltValueNullFieldError.checkNotNull(
              startDate, r'TimeOffCreate', 'startDate'),
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
