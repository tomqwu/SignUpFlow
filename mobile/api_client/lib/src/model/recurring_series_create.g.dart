// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'recurring_series_create.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$RecurringSeriesCreate extends RecurringSeriesCreate {
  @override
  final int duration;
  @override
  final String endConditionType;
  @override
  final Date? endDate;
  @override
  final int? frequencyInterval;
  @override
  final String? location;
  @override
  final int? occurrenceCount;
  @override
  final String patternType;
  @override
  final BuiltMap<String, JsonObject?>? roleRequirements;
  @override
  final BuiltList<String>? selectedDays;
  @override
  final Date startDate;
  @override
  final String startTime;
  @override
  final String title;
  @override
  final String? weekdayName;
  @override
  final String? weekdayPosition;

  factory _$RecurringSeriesCreate(
          [void Function(RecurringSeriesCreateBuilder)? updates]) =>
      (RecurringSeriesCreateBuilder()..update(updates))._build();

  _$RecurringSeriesCreate._(
      {required this.duration,
      required this.endConditionType,
      this.endDate,
      this.frequencyInterval,
      this.location,
      this.occurrenceCount,
      required this.patternType,
      this.roleRequirements,
      this.selectedDays,
      required this.startDate,
      required this.startTime,
      required this.title,
      this.weekdayName,
      this.weekdayPosition})
      : super._();
  @override
  RecurringSeriesCreate rebuild(
          void Function(RecurringSeriesCreateBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  RecurringSeriesCreateBuilder toBuilder() =>
      RecurringSeriesCreateBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is RecurringSeriesCreate &&
        duration == other.duration &&
        endConditionType == other.endConditionType &&
        endDate == other.endDate &&
        frequencyInterval == other.frequencyInterval &&
        location == other.location &&
        occurrenceCount == other.occurrenceCount &&
        patternType == other.patternType &&
        roleRequirements == other.roleRequirements &&
        selectedDays == other.selectedDays &&
        startDate == other.startDate &&
        startTime == other.startTime &&
        title == other.title &&
        weekdayName == other.weekdayName &&
        weekdayPosition == other.weekdayPosition;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, duration.hashCode);
    _$hash = $jc(_$hash, endConditionType.hashCode);
    _$hash = $jc(_$hash, endDate.hashCode);
    _$hash = $jc(_$hash, frequencyInterval.hashCode);
    _$hash = $jc(_$hash, location.hashCode);
    _$hash = $jc(_$hash, occurrenceCount.hashCode);
    _$hash = $jc(_$hash, patternType.hashCode);
    _$hash = $jc(_$hash, roleRequirements.hashCode);
    _$hash = $jc(_$hash, selectedDays.hashCode);
    _$hash = $jc(_$hash, startDate.hashCode);
    _$hash = $jc(_$hash, startTime.hashCode);
    _$hash = $jc(_$hash, title.hashCode);
    _$hash = $jc(_$hash, weekdayName.hashCode);
    _$hash = $jc(_$hash, weekdayPosition.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'RecurringSeriesCreate')
          ..add('duration', duration)
          ..add('endConditionType', endConditionType)
          ..add('endDate', endDate)
          ..add('frequencyInterval', frequencyInterval)
          ..add('location', location)
          ..add('occurrenceCount', occurrenceCount)
          ..add('patternType', patternType)
          ..add('roleRequirements', roleRequirements)
          ..add('selectedDays', selectedDays)
          ..add('startDate', startDate)
          ..add('startTime', startTime)
          ..add('title', title)
          ..add('weekdayName', weekdayName)
          ..add('weekdayPosition', weekdayPosition))
        .toString();
  }
}

class RecurringSeriesCreateBuilder
    implements Builder<RecurringSeriesCreate, RecurringSeriesCreateBuilder> {
  _$RecurringSeriesCreate? _$v;

  int? _duration;
  int? get duration => _$this._duration;
  set duration(int? duration) => _$this._duration = duration;

  String? _endConditionType;
  String? get endConditionType => _$this._endConditionType;
  set endConditionType(String? endConditionType) =>
      _$this._endConditionType = endConditionType;

  Date? _endDate;
  Date? get endDate => _$this._endDate;
  set endDate(Date? endDate) => _$this._endDate = endDate;

  int? _frequencyInterval;
  int? get frequencyInterval => _$this._frequencyInterval;
  set frequencyInterval(int? frequencyInterval) =>
      _$this._frequencyInterval = frequencyInterval;

  String? _location;
  String? get location => _$this._location;
  set location(String? location) => _$this._location = location;

  int? _occurrenceCount;
  int? get occurrenceCount => _$this._occurrenceCount;
  set occurrenceCount(int? occurrenceCount) =>
      _$this._occurrenceCount = occurrenceCount;

  String? _patternType;
  String? get patternType => _$this._patternType;
  set patternType(String? patternType) => _$this._patternType = patternType;

  MapBuilder<String, JsonObject?>? _roleRequirements;
  MapBuilder<String, JsonObject?> get roleRequirements =>
      _$this._roleRequirements ??= MapBuilder<String, JsonObject?>();
  set roleRequirements(MapBuilder<String, JsonObject?>? roleRequirements) =>
      _$this._roleRequirements = roleRequirements;

  ListBuilder<String>? _selectedDays;
  ListBuilder<String> get selectedDays =>
      _$this._selectedDays ??= ListBuilder<String>();
  set selectedDays(ListBuilder<String>? selectedDays) =>
      _$this._selectedDays = selectedDays;

  Date? _startDate;
  Date? get startDate => _$this._startDate;
  set startDate(Date? startDate) => _$this._startDate = startDate;

  String? _startTime;
  String? get startTime => _$this._startTime;
  set startTime(String? startTime) => _$this._startTime = startTime;

  String? _title;
  String? get title => _$this._title;
  set title(String? title) => _$this._title = title;

  String? _weekdayName;
  String? get weekdayName => _$this._weekdayName;
  set weekdayName(String? weekdayName) => _$this._weekdayName = weekdayName;

  String? _weekdayPosition;
  String? get weekdayPosition => _$this._weekdayPosition;
  set weekdayPosition(String? weekdayPosition) =>
      _$this._weekdayPosition = weekdayPosition;

  RecurringSeriesCreateBuilder() {
    RecurringSeriesCreate._defaults(this);
  }

  RecurringSeriesCreateBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _duration = $v.duration;
      _endConditionType = $v.endConditionType;
      _endDate = $v.endDate;
      _frequencyInterval = $v.frequencyInterval;
      _location = $v.location;
      _occurrenceCount = $v.occurrenceCount;
      _patternType = $v.patternType;
      _roleRequirements = $v.roleRequirements?.toBuilder();
      _selectedDays = $v.selectedDays?.toBuilder();
      _startDate = $v.startDate;
      _startTime = $v.startTime;
      _title = $v.title;
      _weekdayName = $v.weekdayName;
      _weekdayPosition = $v.weekdayPosition;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(RecurringSeriesCreate other) {
    _$v = other as _$RecurringSeriesCreate;
  }

  @override
  void update(void Function(RecurringSeriesCreateBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  RecurringSeriesCreate build() => _build();

  _$RecurringSeriesCreate _build() {
    _$RecurringSeriesCreate _$result;
    try {
      _$result = _$v ??
          _$RecurringSeriesCreate._(
            duration: BuiltValueNullFieldError.checkNotNull(
                duration, r'RecurringSeriesCreate', 'duration'),
            endConditionType: BuiltValueNullFieldError.checkNotNull(
                endConditionType, r'RecurringSeriesCreate', 'endConditionType'),
            endDate: endDate,
            frequencyInterval: frequencyInterval,
            location: location,
            occurrenceCount: occurrenceCount,
            patternType: BuiltValueNullFieldError.checkNotNull(
                patternType, r'RecurringSeriesCreate', 'patternType'),
            roleRequirements: _roleRequirements?.build(),
            selectedDays: _selectedDays?.build(),
            startDate: BuiltValueNullFieldError.checkNotNull(
                startDate, r'RecurringSeriesCreate', 'startDate'),
            startTime: BuiltValueNullFieldError.checkNotNull(
                startTime, r'RecurringSeriesCreate', 'startTime'),
            title: BuiltValueNullFieldError.checkNotNull(
                title, r'RecurringSeriesCreate', 'title'),
            weekdayName: weekdayName,
            weekdayPosition: weekdayPosition,
          );
    } catch (_) {
      late String _$failedField;
      try {
        _$failedField = 'roleRequirements';
        _roleRequirements?.build();
        _$failedField = 'selectedDays';
        _selectedDays?.build();
      } catch (e) {
        throw BuiltValueNestedFieldError(
            r'RecurringSeriesCreate', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
