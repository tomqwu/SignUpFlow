// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'holiday_update.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$HolidayUpdate extends HolidayUpdate {
  @override
  final Date? date;
  @override
  final bool? isLongWeekend;
  @override
  final String? label;

  factory _$HolidayUpdate([void Function(HolidayUpdateBuilder)? updates]) =>
      (HolidayUpdateBuilder()..update(updates))._build();

  _$HolidayUpdate._({this.date, this.isLongWeekend, this.label}) : super._();
  @override
  HolidayUpdate rebuild(void Function(HolidayUpdateBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  HolidayUpdateBuilder toBuilder() => HolidayUpdateBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is HolidayUpdate &&
        date == other.date &&
        isLongWeekend == other.isLongWeekend &&
        label == other.label;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, date.hashCode);
    _$hash = $jc(_$hash, isLongWeekend.hashCode);
    _$hash = $jc(_$hash, label.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'HolidayUpdate')
          ..add('date', date)
          ..add('isLongWeekend', isLongWeekend)
          ..add('label', label))
        .toString();
  }
}

class HolidayUpdateBuilder
    implements Builder<HolidayUpdate, HolidayUpdateBuilder> {
  _$HolidayUpdate? _$v;

  Date? _date;
  Date? get date => _$this._date;
  set date(Date? date) => _$this._date = date;

  bool? _isLongWeekend;
  bool? get isLongWeekend => _$this._isLongWeekend;
  set isLongWeekend(bool? isLongWeekend) =>
      _$this._isLongWeekend = isLongWeekend;

  String? _label;
  String? get label => _$this._label;
  set label(String? label) => _$this._label = label;

  HolidayUpdateBuilder() {
    HolidayUpdate._defaults(this);
  }

  HolidayUpdateBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _date = $v.date;
      _isLongWeekend = $v.isLongWeekend;
      _label = $v.label;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(HolidayUpdate other) {
    _$v = other as _$HolidayUpdate;
  }

  @override
  void update(void Function(HolidayUpdateBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  HolidayUpdate build() => _build();

  _$HolidayUpdate _build() {
    final _$result = _$v ??
        _$HolidayUpdate._(
          date: date,
          isLongWeekend: isLongWeekend,
          label: label,
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
