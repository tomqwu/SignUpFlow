// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'holiday_response.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$HolidayResponse extends HolidayResponse {
  @override
  final DateTime createdAt;
  @override
  final Date date;
  @override
  final int id;
  @override
  final bool? isLongWeekend;
  @override
  final String label;
  @override
  final String orgId;

  factory _$HolidayResponse([void Function(HolidayResponseBuilder)? updates]) =>
      (HolidayResponseBuilder()..update(updates))._build();

  _$HolidayResponse._(
      {required this.createdAt,
      required this.date,
      required this.id,
      this.isLongWeekend,
      required this.label,
      required this.orgId})
      : super._();
  @override
  HolidayResponse rebuild(void Function(HolidayResponseBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  HolidayResponseBuilder toBuilder() => HolidayResponseBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is HolidayResponse &&
        createdAt == other.createdAt &&
        date == other.date &&
        id == other.id &&
        isLongWeekend == other.isLongWeekend &&
        label == other.label &&
        orgId == other.orgId;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, createdAt.hashCode);
    _$hash = $jc(_$hash, date.hashCode);
    _$hash = $jc(_$hash, id.hashCode);
    _$hash = $jc(_$hash, isLongWeekend.hashCode);
    _$hash = $jc(_$hash, label.hashCode);
    _$hash = $jc(_$hash, orgId.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'HolidayResponse')
          ..add('createdAt', createdAt)
          ..add('date', date)
          ..add('id', id)
          ..add('isLongWeekend', isLongWeekend)
          ..add('label', label)
          ..add('orgId', orgId))
        .toString();
  }
}

class HolidayResponseBuilder
    implements Builder<HolidayResponse, HolidayResponseBuilder> {
  _$HolidayResponse? _$v;

  DateTime? _createdAt;
  DateTime? get createdAt => _$this._createdAt;
  set createdAt(DateTime? createdAt) => _$this._createdAt = createdAt;

  Date? _date;
  Date? get date => _$this._date;
  set date(Date? date) => _$this._date = date;

  int? _id;
  int? get id => _$this._id;
  set id(int? id) => _$this._id = id;

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

  HolidayResponseBuilder() {
    HolidayResponse._defaults(this);
  }

  HolidayResponseBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _createdAt = $v.createdAt;
      _date = $v.date;
      _id = $v.id;
      _isLongWeekend = $v.isLongWeekend;
      _label = $v.label;
      _orgId = $v.orgId;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(HolidayResponse other) {
    _$v = other as _$HolidayResponse;
  }

  @override
  void update(void Function(HolidayResponseBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  HolidayResponse build() => _build();

  _$HolidayResponse _build() {
    final _$result = _$v ??
        _$HolidayResponse._(
          createdAt: BuiltValueNullFieldError.checkNotNull(
              createdAt, r'HolidayResponse', 'createdAt'),
          date: BuiltValueNullFieldError.checkNotNull(
              date, r'HolidayResponse', 'date'),
          id: BuiltValueNullFieldError.checkNotNull(
              id, r'HolidayResponse', 'id'),
          isLongWeekend: isLongWeekend,
          label: BuiltValueNullFieldError.checkNotNull(
              label, r'HolidayResponse', 'label'),
          orgId: BuiltValueNullFieldError.checkNotNull(
              orgId, r'HolidayResponse', 'orgId'),
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
