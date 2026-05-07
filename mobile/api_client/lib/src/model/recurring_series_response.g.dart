// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'recurring_series_response.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$RecurringSeriesResponse extends RecurringSeriesResponse {
  @override
  final bool active;
  @override
  final DateTime createdAt;
  @override
  final String createdBy;
  @override
  final int duration;
  @override
  final String endConditionType;
  @override
  final Date? endDate;
  @override
  final int? frequencyInterval;
  @override
  final String id;
  @override
  final String? location;
  @override
  final int? occurrenceCount;
  @override
  final int? occurrencePreviewCount;
  @override
  final String orgId;
  @override
  final String patternType;
  @override
  final BuiltMap<String, JsonObject?>? roleRequirements;
  @override
  final BuiltList<String>? selectedDays;
  @override
  final Date startDate;
  @override
  final String title;
  @override
  final DateTime updatedAt;
  @override
  final String? weekdayName;
  @override
  final String? weekdayPosition;

  factory _$RecurringSeriesResponse(
          [void Function(RecurringSeriesResponseBuilder)? updates]) =>
      (RecurringSeriesResponseBuilder()..update(updates))._build();

  _$RecurringSeriesResponse._(
      {required this.active,
      required this.createdAt,
      required this.createdBy,
      required this.duration,
      required this.endConditionType,
      this.endDate,
      this.frequencyInterval,
      required this.id,
      this.location,
      this.occurrenceCount,
      this.occurrencePreviewCount,
      required this.orgId,
      required this.patternType,
      this.roleRequirements,
      this.selectedDays,
      required this.startDate,
      required this.title,
      required this.updatedAt,
      this.weekdayName,
      this.weekdayPosition})
      : super._();
  @override
  RecurringSeriesResponse rebuild(
          void Function(RecurringSeriesResponseBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  RecurringSeriesResponseBuilder toBuilder() =>
      RecurringSeriesResponseBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is RecurringSeriesResponse &&
        active == other.active &&
        createdAt == other.createdAt &&
        createdBy == other.createdBy &&
        duration == other.duration &&
        endConditionType == other.endConditionType &&
        endDate == other.endDate &&
        frequencyInterval == other.frequencyInterval &&
        id == other.id &&
        location == other.location &&
        occurrenceCount == other.occurrenceCount &&
        occurrencePreviewCount == other.occurrencePreviewCount &&
        orgId == other.orgId &&
        patternType == other.patternType &&
        roleRequirements == other.roleRequirements &&
        selectedDays == other.selectedDays &&
        startDate == other.startDate &&
        title == other.title &&
        updatedAt == other.updatedAt &&
        weekdayName == other.weekdayName &&
        weekdayPosition == other.weekdayPosition;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, active.hashCode);
    _$hash = $jc(_$hash, createdAt.hashCode);
    _$hash = $jc(_$hash, createdBy.hashCode);
    _$hash = $jc(_$hash, duration.hashCode);
    _$hash = $jc(_$hash, endConditionType.hashCode);
    _$hash = $jc(_$hash, endDate.hashCode);
    _$hash = $jc(_$hash, frequencyInterval.hashCode);
    _$hash = $jc(_$hash, id.hashCode);
    _$hash = $jc(_$hash, location.hashCode);
    _$hash = $jc(_$hash, occurrenceCount.hashCode);
    _$hash = $jc(_$hash, occurrencePreviewCount.hashCode);
    _$hash = $jc(_$hash, orgId.hashCode);
    _$hash = $jc(_$hash, patternType.hashCode);
    _$hash = $jc(_$hash, roleRequirements.hashCode);
    _$hash = $jc(_$hash, selectedDays.hashCode);
    _$hash = $jc(_$hash, startDate.hashCode);
    _$hash = $jc(_$hash, title.hashCode);
    _$hash = $jc(_$hash, updatedAt.hashCode);
    _$hash = $jc(_$hash, weekdayName.hashCode);
    _$hash = $jc(_$hash, weekdayPosition.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'RecurringSeriesResponse')
          ..add('active', active)
          ..add('createdAt', createdAt)
          ..add('createdBy', createdBy)
          ..add('duration', duration)
          ..add('endConditionType', endConditionType)
          ..add('endDate', endDate)
          ..add('frequencyInterval', frequencyInterval)
          ..add('id', id)
          ..add('location', location)
          ..add('occurrenceCount', occurrenceCount)
          ..add('occurrencePreviewCount', occurrencePreviewCount)
          ..add('orgId', orgId)
          ..add('patternType', patternType)
          ..add('roleRequirements', roleRequirements)
          ..add('selectedDays', selectedDays)
          ..add('startDate', startDate)
          ..add('title', title)
          ..add('updatedAt', updatedAt)
          ..add('weekdayName', weekdayName)
          ..add('weekdayPosition', weekdayPosition))
        .toString();
  }
}

class RecurringSeriesResponseBuilder
    implements
        Builder<RecurringSeriesResponse, RecurringSeriesResponseBuilder> {
  _$RecurringSeriesResponse? _$v;

  bool? _active;
  bool? get active => _$this._active;
  set active(bool? active) => _$this._active = active;

  DateTime? _createdAt;
  DateTime? get createdAt => _$this._createdAt;
  set createdAt(DateTime? createdAt) => _$this._createdAt = createdAt;

  String? _createdBy;
  String? get createdBy => _$this._createdBy;
  set createdBy(String? createdBy) => _$this._createdBy = createdBy;

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

  String? _id;
  String? get id => _$this._id;
  set id(String? id) => _$this._id = id;

  String? _location;
  String? get location => _$this._location;
  set location(String? location) => _$this._location = location;

  int? _occurrenceCount;
  int? get occurrenceCount => _$this._occurrenceCount;
  set occurrenceCount(int? occurrenceCount) =>
      _$this._occurrenceCount = occurrenceCount;

  int? _occurrencePreviewCount;
  int? get occurrencePreviewCount => _$this._occurrencePreviewCount;
  set occurrencePreviewCount(int? occurrencePreviewCount) =>
      _$this._occurrencePreviewCount = occurrencePreviewCount;

  String? _orgId;
  String? get orgId => _$this._orgId;
  set orgId(String? orgId) => _$this._orgId = orgId;

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

  String? _title;
  String? get title => _$this._title;
  set title(String? title) => _$this._title = title;

  DateTime? _updatedAt;
  DateTime? get updatedAt => _$this._updatedAt;
  set updatedAt(DateTime? updatedAt) => _$this._updatedAt = updatedAt;

  String? _weekdayName;
  String? get weekdayName => _$this._weekdayName;
  set weekdayName(String? weekdayName) => _$this._weekdayName = weekdayName;

  String? _weekdayPosition;
  String? get weekdayPosition => _$this._weekdayPosition;
  set weekdayPosition(String? weekdayPosition) =>
      _$this._weekdayPosition = weekdayPosition;

  RecurringSeriesResponseBuilder() {
    RecurringSeriesResponse._defaults(this);
  }

  RecurringSeriesResponseBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _active = $v.active;
      _createdAt = $v.createdAt;
      _createdBy = $v.createdBy;
      _duration = $v.duration;
      _endConditionType = $v.endConditionType;
      _endDate = $v.endDate;
      _frequencyInterval = $v.frequencyInterval;
      _id = $v.id;
      _location = $v.location;
      _occurrenceCount = $v.occurrenceCount;
      _occurrencePreviewCount = $v.occurrencePreviewCount;
      _orgId = $v.orgId;
      _patternType = $v.patternType;
      _roleRequirements = $v.roleRequirements?.toBuilder();
      _selectedDays = $v.selectedDays?.toBuilder();
      _startDate = $v.startDate;
      _title = $v.title;
      _updatedAt = $v.updatedAt;
      _weekdayName = $v.weekdayName;
      _weekdayPosition = $v.weekdayPosition;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(RecurringSeriesResponse other) {
    _$v = other as _$RecurringSeriesResponse;
  }

  @override
  void update(void Function(RecurringSeriesResponseBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  RecurringSeriesResponse build() => _build();

  _$RecurringSeriesResponse _build() {
    _$RecurringSeriesResponse _$result;
    try {
      _$result = _$v ??
          _$RecurringSeriesResponse._(
            active: BuiltValueNullFieldError.checkNotNull(
                active, r'RecurringSeriesResponse', 'active'),
            createdAt: BuiltValueNullFieldError.checkNotNull(
                createdAt, r'RecurringSeriesResponse', 'createdAt'),
            createdBy: BuiltValueNullFieldError.checkNotNull(
                createdBy, r'RecurringSeriesResponse', 'createdBy'),
            duration: BuiltValueNullFieldError.checkNotNull(
                duration, r'RecurringSeriesResponse', 'duration'),
            endConditionType: BuiltValueNullFieldError.checkNotNull(
                endConditionType,
                r'RecurringSeriesResponse',
                'endConditionType'),
            endDate: endDate,
            frequencyInterval: frequencyInterval,
            id: BuiltValueNullFieldError.checkNotNull(
                id, r'RecurringSeriesResponse', 'id'),
            location: location,
            occurrenceCount: occurrenceCount,
            occurrencePreviewCount: occurrencePreviewCount,
            orgId: BuiltValueNullFieldError.checkNotNull(
                orgId, r'RecurringSeriesResponse', 'orgId'),
            patternType: BuiltValueNullFieldError.checkNotNull(
                patternType, r'RecurringSeriesResponse', 'patternType'),
            roleRequirements: _roleRequirements?.build(),
            selectedDays: _selectedDays?.build(),
            startDate: BuiltValueNullFieldError.checkNotNull(
                startDate, r'RecurringSeriesResponse', 'startDate'),
            title: BuiltValueNullFieldError.checkNotNull(
                title, r'RecurringSeriesResponse', 'title'),
            updatedAt: BuiltValueNullFieldError.checkNotNull(
                updatedAt, r'RecurringSeriesResponse', 'updatedAt'),
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
            r'RecurringSeriesResponse', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
