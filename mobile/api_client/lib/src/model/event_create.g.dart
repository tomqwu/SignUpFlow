// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'event_create.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$EventCreate extends EventCreate {
  @override
  final DateTime endTime;
  @override
  final BuiltMap<String, JsonObject?>? extraData;
  @override
  final String id;
  @override
  final String orgId;
  @override
  final String? resourceId;
  @override
  final DateTime startTime;
  @override
  final BuiltList<String>? teamIds;
  @override
  final String type;

  factory _$EventCreate([void Function(EventCreateBuilder)? updates]) =>
      (EventCreateBuilder()..update(updates))._build();

  _$EventCreate._(
      {required this.endTime,
      this.extraData,
      required this.id,
      required this.orgId,
      this.resourceId,
      required this.startTime,
      this.teamIds,
      required this.type})
      : super._();
  @override
  EventCreate rebuild(void Function(EventCreateBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  EventCreateBuilder toBuilder() => EventCreateBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is EventCreate &&
        endTime == other.endTime &&
        extraData == other.extraData &&
        id == other.id &&
        orgId == other.orgId &&
        resourceId == other.resourceId &&
        startTime == other.startTime &&
        teamIds == other.teamIds &&
        type == other.type;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, endTime.hashCode);
    _$hash = $jc(_$hash, extraData.hashCode);
    _$hash = $jc(_$hash, id.hashCode);
    _$hash = $jc(_$hash, orgId.hashCode);
    _$hash = $jc(_$hash, resourceId.hashCode);
    _$hash = $jc(_$hash, startTime.hashCode);
    _$hash = $jc(_$hash, teamIds.hashCode);
    _$hash = $jc(_$hash, type.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'EventCreate')
          ..add('endTime', endTime)
          ..add('extraData', extraData)
          ..add('id', id)
          ..add('orgId', orgId)
          ..add('resourceId', resourceId)
          ..add('startTime', startTime)
          ..add('teamIds', teamIds)
          ..add('type', type))
        .toString();
  }
}

class EventCreateBuilder implements Builder<EventCreate, EventCreateBuilder> {
  _$EventCreate? _$v;

  DateTime? _endTime;
  DateTime? get endTime => _$this._endTime;
  set endTime(DateTime? endTime) => _$this._endTime = endTime;

  MapBuilder<String, JsonObject?>? _extraData;
  MapBuilder<String, JsonObject?> get extraData =>
      _$this._extraData ??= MapBuilder<String, JsonObject?>();
  set extraData(MapBuilder<String, JsonObject?>? extraData) =>
      _$this._extraData = extraData;

  String? _id;
  String? get id => _$this._id;
  set id(String? id) => _$this._id = id;

  String? _orgId;
  String? get orgId => _$this._orgId;
  set orgId(String? orgId) => _$this._orgId = orgId;

  String? _resourceId;
  String? get resourceId => _$this._resourceId;
  set resourceId(String? resourceId) => _$this._resourceId = resourceId;

  DateTime? _startTime;
  DateTime? get startTime => _$this._startTime;
  set startTime(DateTime? startTime) => _$this._startTime = startTime;

  ListBuilder<String>? _teamIds;
  ListBuilder<String> get teamIds => _$this._teamIds ??= ListBuilder<String>();
  set teamIds(ListBuilder<String>? teamIds) => _$this._teamIds = teamIds;

  String? _type;
  String? get type => _$this._type;
  set type(String? type) => _$this._type = type;

  EventCreateBuilder() {
    EventCreate._defaults(this);
  }

  EventCreateBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _endTime = $v.endTime;
      _extraData = $v.extraData?.toBuilder();
      _id = $v.id;
      _orgId = $v.orgId;
      _resourceId = $v.resourceId;
      _startTime = $v.startTime;
      _teamIds = $v.teamIds?.toBuilder();
      _type = $v.type;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(EventCreate other) {
    _$v = other as _$EventCreate;
  }

  @override
  void update(void Function(EventCreateBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  EventCreate build() => _build();

  _$EventCreate _build() {
    _$EventCreate _$result;
    try {
      _$result = _$v ??
          _$EventCreate._(
            endTime: BuiltValueNullFieldError.checkNotNull(
                endTime, r'EventCreate', 'endTime'),
            extraData: _extraData?.build(),
            id: BuiltValueNullFieldError.checkNotNull(id, r'EventCreate', 'id'),
            orgId: BuiltValueNullFieldError.checkNotNull(
                orgId, r'EventCreate', 'orgId'),
            resourceId: resourceId,
            startTime: BuiltValueNullFieldError.checkNotNull(
                startTime, r'EventCreate', 'startTime'),
            teamIds: _teamIds?.build(),
            type: BuiltValueNullFieldError.checkNotNull(
                type, r'EventCreate', 'type'),
          );
    } catch (_) {
      late String _$failedField;
      try {
        _$failedField = 'extraData';
        _extraData?.build();

        _$failedField = 'teamIds';
        _teamIds?.build();
      } catch (e) {
        throw BuiltValueNestedFieldError(
            r'EventCreate', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
