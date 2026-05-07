// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'preview_request.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$PreviewRequest extends PreviewRequest {
  @override
  final int duration;
  @override
  final String endConditionType;
  @override
  final Date? endDate;
  @override
  final int? frequencyInterval;
  @override
  final int? occurrenceCount;
  @override
  final String patternType;
  @override
  final BuiltList<String>? selectedDays;
  @override
  final Date startDate;
  @override
  final String startTime;
  @override
  final String? weekdayName;
  @override
  final String? weekdayPosition;

  factory _$PreviewRequest([void Function(PreviewRequestBuilder)? updates]) =>
      (PreviewRequestBuilder()..update(updates))._build();

  _$PreviewRequest._(
      {required this.duration,
      required this.endConditionType,
      this.endDate,
      this.frequencyInterval,
      this.occurrenceCount,
      required this.patternType,
      this.selectedDays,
      required this.startDate,
      required this.startTime,
      this.weekdayName,
      this.weekdayPosition})
      : super._();
  @override
  PreviewRequest rebuild(void Function(PreviewRequestBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  PreviewRequestBuilder toBuilder() => PreviewRequestBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is PreviewRequest &&
        duration == other.duration &&
        endConditionType == other.endConditionType &&
        endDate == other.endDate &&
        frequencyInterval == other.frequencyInterval &&
        occurrenceCount == other.occurrenceCount &&
        patternType == other.patternType &&
        selectedDays == other.selectedDays &&
        startDate == other.startDate &&
        startTime == other.startTime &&
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
    _$hash = $jc(_$hash, occurrenceCount.hashCode);
    _$hash = $jc(_$hash, patternType.hashCode);
    _$hash = $jc(_$hash, selectedDays.hashCode);
    _$hash = $jc(_$hash, startDate.hashCode);
    _$hash = $jc(_$hash, startTime.hashCode);
    _$hash = $jc(_$hash, weekdayName.hashCode);
    _$hash = $jc(_$hash, weekdayPosition.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'PreviewRequest')
          ..add('duration', duration)
          ..add('endConditionType', endConditionType)
          ..add('endDate', endDate)
          ..add('frequencyInterval', frequencyInterval)
          ..add('occurrenceCount', occurrenceCount)
          ..add('patternType', patternType)
          ..add('selectedDays', selectedDays)
          ..add('startDate', startDate)
          ..add('startTime', startTime)
          ..add('weekdayName', weekdayName)
          ..add('weekdayPosition', weekdayPosition))
        .toString();
  }
}

class PreviewRequestBuilder
    implements Builder<PreviewRequest, PreviewRequestBuilder> {
  _$PreviewRequest? _$v;

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

  int? _occurrenceCount;
  int? get occurrenceCount => _$this._occurrenceCount;
  set occurrenceCount(int? occurrenceCount) =>
      _$this._occurrenceCount = occurrenceCount;

  String? _patternType;
  String? get patternType => _$this._patternType;
  set patternType(String? patternType) => _$this._patternType = patternType;

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

  String? _weekdayName;
  String? get weekdayName => _$this._weekdayName;
  set weekdayName(String? weekdayName) => _$this._weekdayName = weekdayName;

  String? _weekdayPosition;
  String? get weekdayPosition => _$this._weekdayPosition;
  set weekdayPosition(String? weekdayPosition) =>
      _$this._weekdayPosition = weekdayPosition;

  PreviewRequestBuilder() {
    PreviewRequest._defaults(this);
  }

  PreviewRequestBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _duration = $v.duration;
      _endConditionType = $v.endConditionType;
      _endDate = $v.endDate;
      _frequencyInterval = $v.frequencyInterval;
      _occurrenceCount = $v.occurrenceCount;
      _patternType = $v.patternType;
      _selectedDays = $v.selectedDays?.toBuilder();
      _startDate = $v.startDate;
      _startTime = $v.startTime;
      _weekdayName = $v.weekdayName;
      _weekdayPosition = $v.weekdayPosition;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(PreviewRequest other) {
    _$v = other as _$PreviewRequest;
  }

  @override
  void update(void Function(PreviewRequestBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  PreviewRequest build() => _build();

  _$PreviewRequest _build() {
    _$PreviewRequest _$result;
    try {
      _$result = _$v ??
          _$PreviewRequest._(
            duration: BuiltValueNullFieldError.checkNotNull(
                duration, r'PreviewRequest', 'duration'),
            endConditionType: BuiltValueNullFieldError.checkNotNull(
                endConditionType, r'PreviewRequest', 'endConditionType'),
            endDate: endDate,
            frequencyInterval: frequencyInterval,
            occurrenceCount: occurrenceCount,
            patternType: BuiltValueNullFieldError.checkNotNull(
                patternType, r'PreviewRequest', 'patternType'),
            selectedDays: _selectedDays?.build(),
            startDate: BuiltValueNullFieldError.checkNotNull(
                startDate, r'PreviewRequest', 'startDate'),
            startTime: BuiltValueNullFieldError.checkNotNull(
                startTime, r'PreviewRequest', 'startTime'),
            weekdayName: weekdayName,
            weekdayPosition: weekdayPosition,
          );
    } catch (_) {
      late String _$failedField;
      try {
        _$failedField = 'selectedDays';
        _selectedDays?.build();
      } catch (e) {
        throw BuiltValueNestedFieldError(
            r'PreviewRequest', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
