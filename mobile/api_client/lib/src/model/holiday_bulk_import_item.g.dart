// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'holiday_bulk_import_item.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$HolidayBulkImportItem extends HolidayBulkImportItem {
  @override
  final Date date;
  @override
  final bool? isLongWeekend;
  @override
  final String label;

  factory _$HolidayBulkImportItem(
          [void Function(HolidayBulkImportItemBuilder)? updates]) =>
      (HolidayBulkImportItemBuilder()..update(updates))._build();

  _$HolidayBulkImportItem._(
      {required this.date, this.isLongWeekend, required this.label})
      : super._();
  @override
  HolidayBulkImportItem rebuild(
          void Function(HolidayBulkImportItemBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  HolidayBulkImportItemBuilder toBuilder() =>
      HolidayBulkImportItemBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is HolidayBulkImportItem &&
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
    return (newBuiltValueToStringHelper(r'HolidayBulkImportItem')
          ..add('date', date)
          ..add('isLongWeekend', isLongWeekend)
          ..add('label', label))
        .toString();
  }
}

class HolidayBulkImportItemBuilder
    implements Builder<HolidayBulkImportItem, HolidayBulkImportItemBuilder> {
  _$HolidayBulkImportItem? _$v;

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

  HolidayBulkImportItemBuilder() {
    HolidayBulkImportItem._defaults(this);
  }

  HolidayBulkImportItemBuilder get _$this {
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
  void replace(HolidayBulkImportItem other) {
    _$v = other as _$HolidayBulkImportItem;
  }

  @override
  void update(void Function(HolidayBulkImportItemBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  HolidayBulkImportItem build() => _build();

  _$HolidayBulkImportItem _build() {
    final _$result = _$v ??
        _$HolidayBulkImportItem._(
          date: BuiltValueNullFieldError.checkNotNull(
              date, r'HolidayBulkImportItem', 'date'),
          isLongWeekend: isLongWeekend,
          label: BuiltValueNullFieldError.checkNotNull(
              label, r'HolidayBulkImportItem', 'label'),
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
