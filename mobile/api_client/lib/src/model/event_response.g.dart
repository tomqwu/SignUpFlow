// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'event_response.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$EventResponse extends EventResponse {
  @override
  final DateTime createdAt;
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
  final String type;
  @override
  final DateTime updatedAt;

  factory _$EventResponse([void Function(EventResponseBuilder)? updates]) =>
      (EventResponseBuilder()..update(updates))._build();

  _$EventResponse._(
      {required this.createdAt,
      required this.endTime,
      this.extraData,
      required this.id,
      required this.orgId,
      this.resourceId,
      required this.startTime,
      required this.type,
      required this.updatedAt})
      : super._();
  @override
  EventResponse rebuild(void Function(EventResponseBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  EventResponseBuilder toBuilder() => EventResponseBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is EventResponse &&
        createdAt == other.createdAt &&
        endTime == other.endTime &&
        extraData == other.extraData &&
        id == other.id &&
        orgId == other.orgId &&
        resourceId == other.resourceId &&
        startTime == other.startTime &&
        type == other.type &&
        updatedAt == other.updatedAt;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, createdAt.hashCode);
    _$hash = $jc(_$hash, endTime.hashCode);
    _$hash = $jc(_$hash, extraData.hashCode);
    _$hash = $jc(_$hash, id.hashCode);
    _$hash = $jc(_$hash, orgId.hashCode);
    _$hash = $jc(_$hash, resourceId.hashCode);
    _$hash = $jc(_$hash, startTime.hashCode);
    _$hash = $jc(_$hash, type.hashCode);
    _$hash = $jc(_$hash, updatedAt.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'EventResponse')
          ..add('createdAt', createdAt)
          ..add('endTime', endTime)
          ..add('extraData', extraData)
          ..add('id', id)
          ..add('orgId', orgId)
          ..add('resourceId', resourceId)
          ..add('startTime', startTime)
          ..add('type', type)
          ..add('updatedAt', updatedAt))
        .toString();
  }
}

class EventResponseBuilder
    implements Builder<EventResponse, EventResponseBuilder> {
  _$EventResponse? _$v;

  DateTime? _createdAt;
  DateTime? get createdAt => _$this._createdAt;
  set createdAt(DateTime? createdAt) => _$this._createdAt = createdAt;

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

  String? _type;
  String? get type => _$this._type;
  set type(String? type) => _$this._type = type;

  DateTime? _updatedAt;
  DateTime? get updatedAt => _$this._updatedAt;
  set updatedAt(DateTime? updatedAt) => _$this._updatedAt = updatedAt;

  EventResponseBuilder() {
    EventResponse._defaults(this);
  }

  EventResponseBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _createdAt = $v.createdAt;
      _endTime = $v.endTime;
      _extraData = $v.extraData?.toBuilder();
      _id = $v.id;
      _orgId = $v.orgId;
      _resourceId = $v.resourceId;
      _startTime = $v.startTime;
      _type = $v.type;
      _updatedAt = $v.updatedAt;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(EventResponse other) {
    _$v = other as _$EventResponse;
  }

  @override
  void update(void Function(EventResponseBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  EventResponse build() => _build();

  _$EventResponse _build() {
    _$EventResponse _$result;
    try {
      _$result = _$v ??
          _$EventResponse._(
            createdAt: BuiltValueNullFieldError.checkNotNull(
                createdAt, r'EventResponse', 'createdAt'),
            endTime: BuiltValueNullFieldError.checkNotNull(
                endTime, r'EventResponse', 'endTime'),
            extraData: _extraData?.build(),
            id: BuiltValueNullFieldError.checkNotNull(
                id, r'EventResponse', 'id'),
            orgId: BuiltValueNullFieldError.checkNotNull(
                orgId, r'EventResponse', 'orgId'),
            resourceId: resourceId,
            startTime: BuiltValueNullFieldError.checkNotNull(
                startTime, r'EventResponse', 'startTime'),
            type: BuiltValueNullFieldError.checkNotNull(
                type, r'EventResponse', 'type'),
            updatedAt: BuiltValueNullFieldError.checkNotNull(
                updatedAt, r'EventResponse', 'updatedAt'),
          );
    } catch (_) {
      late String _$failedField;
      try {
        _$failedField = 'extraData';
        _extraData?.build();
      } catch (e) {
        throw BuiltValueNestedFieldError(
            r'EventResponse', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
