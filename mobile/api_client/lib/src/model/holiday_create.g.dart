// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'holiday_create.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$HolidayCreate extends HolidayCreate {
  @override
  final Date date;
  @override
  final bool? isLongWeekend;
  @override
  final String label;
  @override
  final String orgId;

  factory _$HolidayCreate([void Function(HolidayCreateBuilder)? updates]) =>
      (HolidayCreateBuilder()..update(updates))._build();

  _$HolidayCreate._(
      {required this.date,
      this.isLongWeekend,
      required this.label,
      required this.orgId})
      : super._();
  @override
  HolidayCreate rebuild(void Function(HolidayCreateBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  HolidayCreateBuilder toBuilder() => HolidayCreateBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is HolidayCreate &&
        date == other.date &&
        isLongWeekend == other.isLongWeekend &&
        label == other.label &&
        orgId == other.orgId;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, date.hashCode);
    _$hash = $jc(_$hash, isLongWeekend.hashCode);
    _$hash = $jc(_$hash, label.hashCode);
    _$hash = $jc(_$hash, orgId.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'HolidayCreate')
          ..add('date', date)
          ..add('isLongWeekend', isLongWeekend)
          ..add('label', label)
          ..add('orgId', orgId))
        .toString();
  }
}

class HolidayCreateBuilder
    implements Builder<HolidayCreate, HolidayCreateBuilder> {
  _$HolidayCreate? _$v;

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

  String? _orgId;
  String? get orgId => _$this._orgId;
  set orgId(String? orgId) => _$this._orgId = orgId;

  HolidayCreateBuilder() {
    HolidayCreate._defaults(this);
  }

  HolidayCreateBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _date = $v.date;
      _isLongWeekend = $v.isLongWeekend;
      _label = $v.label;
      _orgId = $v.orgId;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(HolidayCreate other) {
    _$v = other as _$HolidayCreate;
  }

  @override
  void update(void Function(HolidayCreateBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  HolidayCreate build() => _build();

  _$HolidayCreate _build() {
    final _$result = _$v ??
        _$HolidayCreate._(
          date: BuiltValueNullFieldError.checkNotNull(
              date, r'HolidayCreate', 'date'),
          isLongWeekend: isLongWeekend,
          label: BuiltValueNullFieldError.checkNotNull(
              label, r'HolidayCreate', 'label'),
          orgId: BuiltValueNullFieldError.checkNotNull(
              orgId, r'HolidayCreate', 'orgId'),
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
