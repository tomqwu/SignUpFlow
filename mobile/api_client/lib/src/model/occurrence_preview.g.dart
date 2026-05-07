// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'occurrence_preview.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$OccurrencePreview extends OccurrencePreview {
  @override
  final DateTime endTime;
  @override
  final String? holidayLabel;
  @override
  final bool? isHolidayConflict;
  @override
  final String? location;
  @override
  final int occurrenceSequence;
  @override
  final BuiltMap<String, JsonObject?>? roleRequirements;
  @override
  final DateTime startTime;
  @override
  final String title;

  factory _$OccurrencePreview(
          [void Function(OccurrencePreviewBuilder)? updates]) =>
      (OccurrencePreviewBuilder()..update(updates))._build();

  _$OccurrencePreview._(
      {required this.endTime,
      this.holidayLabel,
      this.isHolidayConflict,
      this.location,
      required this.occurrenceSequence,
      this.roleRequirements,
      required this.startTime,
      required this.title})
      : super._();
  @override
  OccurrencePreview rebuild(void Function(OccurrencePreviewBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  OccurrencePreviewBuilder toBuilder() =>
      OccurrencePreviewBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is OccurrencePreview &&
        endTime == other.endTime &&
        holidayLabel == other.holidayLabel &&
        isHolidayConflict == other.isHolidayConflict &&
        location == other.location &&
        occurrenceSequence == other.occurrenceSequence &&
        roleRequirements == other.roleRequirements &&
        startTime == other.startTime &&
        title == other.title;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, endTime.hashCode);
    _$hash = $jc(_$hash, holidayLabel.hashCode);
    _$hash = $jc(_$hash, isHolidayConflict.hashCode);
    _$hash = $jc(_$hash, location.hashCode);
    _$hash = $jc(_$hash, occurrenceSequence.hashCode);
    _$hash = $jc(_$hash, roleRequirements.hashCode);
    _$hash = $jc(_$hash, startTime.hashCode);
    _$hash = $jc(_$hash, title.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'OccurrencePreview')
          ..add('endTime', endTime)
          ..add('holidayLabel', holidayLabel)
          ..add('isHolidayConflict', isHolidayConflict)
          ..add('location', location)
          ..add('occurrenceSequence', occurrenceSequence)
          ..add('roleRequirements', roleRequirements)
          ..add('startTime', startTime)
          ..add('title', title))
        .toString();
  }
}

class OccurrencePreviewBuilder
    implements Builder<OccurrencePreview, OccurrencePreviewBuilder> {
  _$OccurrencePreview? _$v;

  DateTime? _endTime;
  DateTime? get endTime => _$this._endTime;
  set endTime(DateTime? endTime) => _$this._endTime = endTime;

  String? _holidayLabel;
  String? get holidayLabel => _$this._holidayLabel;
  set holidayLabel(String? holidayLabel) => _$this._holidayLabel = holidayLabel;

  bool? _isHolidayConflict;
  bool? get isHolidayConflict => _$this._isHolidayConflict;
  set isHolidayConflict(bool? isHolidayConflict) =>
      _$this._isHolidayConflict = isHolidayConflict;

  String? _location;
  String? get location => _$this._location;
  set location(String? location) => _$this._location = location;

  int? _occurrenceSequence;
  int? get occurrenceSequence => _$this._occurrenceSequence;
  set occurrenceSequence(int? occurrenceSequence) =>
      _$this._occurrenceSequence = occurrenceSequence;

  MapBuilder<String, JsonObject?>? _roleRequirements;
  MapBuilder<String, JsonObject?> get roleRequirements =>
      _$this._roleRequirements ??= MapBuilder<String, JsonObject?>();
  set roleRequirements(MapBuilder<String, JsonObject?>? roleRequirements) =>
      _$this._roleRequirements = roleRequirements;

  DateTime? _startTime;
  DateTime? get startTime => _$this._startTime;
  set startTime(DateTime? startTime) => _$this._startTime = startTime;

  String? _title;
  String? get title => _$this._title;
  set title(String? title) => _$this._title = title;

  OccurrencePreviewBuilder() {
    OccurrencePreview._defaults(this);
  }

  OccurrencePreviewBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _endTime = $v.endTime;
      _holidayLabel = $v.holidayLabel;
      _isHolidayConflict = $v.isHolidayConflict;
      _location = $v.location;
      _occurrenceSequence = $v.occurrenceSequence;
      _roleRequirements = $v.roleRequirements?.toBuilder();
      _startTime = $v.startTime;
      _title = $v.title;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(OccurrencePreview other) {
    _$v = other as _$OccurrencePreview;
  }

  @override
  void update(void Function(OccurrencePreviewBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  OccurrencePreview build() => _build();

  _$OccurrencePreview _build() {
    _$OccurrencePreview _$result;
    try {
      _$result = _$v ??
          _$OccurrencePreview._(
            endTime: BuiltValueNullFieldError.checkNotNull(
                endTime, r'OccurrencePreview', 'endTime'),
            holidayLabel: holidayLabel,
            isHolidayConflict: isHolidayConflict,
            location: location,
            occurrenceSequence: BuiltValueNullFieldError.checkNotNull(
                occurrenceSequence, r'OccurrencePreview', 'occurrenceSequence'),
            roleRequirements: _roleRequirements?.build(),
            startTime: BuiltValueNullFieldError.checkNotNull(
                startTime, r'OccurrencePreview', 'startTime'),
            title: BuiltValueNullFieldError.checkNotNull(
                title, r'OccurrencePreview', 'title'),
          );
    } catch (_) {
      late String _$failedField;
      try {
        _$failedField = 'roleRequirements';
        _roleRequirements?.build();
      } catch (e) {
        throw BuiltValueNestedFieldError(
            r'OccurrencePreview', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
