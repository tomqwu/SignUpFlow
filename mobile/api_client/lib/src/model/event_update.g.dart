// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'event_update.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$EventUpdate extends EventUpdate {
  @override
  final DateTime? endTime;
  @override
  final BuiltMap<String, JsonObject?>? extraData;
  @override
  final String? resourceId;
  @override
  final DateTime? startTime;
  @override
  final String? type;

  factory _$EventUpdate([void Function(EventUpdateBuilder)? updates]) =>
      (EventUpdateBuilder()..update(updates))._build();

  _$EventUpdate._(
      {this.endTime,
      this.extraData,
      this.resourceId,
      this.startTime,
      this.type})
      : super._();
  @override
  EventUpdate rebuild(void Function(EventUpdateBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  EventUpdateBuilder toBuilder() => EventUpdateBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is EventUpdate &&
        endTime == other.endTime &&
        extraData == other.extraData &&
        resourceId == other.resourceId &&
        startTime == other.startTime &&
        type == other.type;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, endTime.hashCode);
    _$hash = $jc(_$hash, extraData.hashCode);
    _$hash = $jc(_$hash, resourceId.hashCode);
    _$hash = $jc(_$hash, startTime.hashCode);
    _$hash = $jc(_$hash, type.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'EventUpdate')
          ..add('endTime', endTime)
          ..add('extraData', extraData)
          ..add('resourceId', resourceId)
          ..add('startTime', startTime)
          ..add('type', type))
        .toString();
  }
}

class EventUpdateBuilder implements Builder<EventUpdate, EventUpdateBuilder> {
  _$EventUpdate? _$v;

  DateTime? _endTime;
  DateTime? get endTime => _$this._endTime;
  set endTime(DateTime? endTime) => _$this._endTime = endTime;

  MapBuilder<String, JsonObject?>? _extraData;
  MapBuilder<String, JsonObject?> get extraData =>
      _$this._extraData ??= MapBuilder<String, JsonObject?>();
  set extraData(MapBuilder<String, JsonObject?>? extraData) =>
      _$this._extraData = extraData;

  String? _resourceId;
  String? get resourceId => _$this._resourceId;
  set resourceId(String? resourceId) => _$this._resourceId = resourceId;

  DateTime? _startTime;
  DateTime? get startTime => _$this._startTime;
  set startTime(DateTime? startTime) => _$this._startTime = startTime;

  String? _type;
  String? get type => _$this._type;
  set type(String? type) => _$this._type = type;

  EventUpdateBuilder() {
    EventUpdate._defaults(this);
  }

  EventUpdateBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _endTime = $v.endTime;
      _extraData = $v.extraData?.toBuilder();
      _resourceId = $v.resourceId;
      _startTime = $v.startTime;
      _type = $v.type;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(EventUpdate other) {
    _$v = other as _$EventUpdate;
  }

  @override
  void update(void Function(EventUpdateBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  EventUpdate build() => _build();

  _$EventUpdate _build() {
    _$EventUpdate _$result;
    try {
      _$result = _$v ??
          _$EventUpdate._(
            endTime: endTime,
            extraData: _extraData?.build(),
            resourceId: resourceId,
            startTime: startTime,
            type: type,
          );
    } catch (_) {
      late String _$failedField;
      try {
        _$failedField = 'extraData';
        _extraData?.build();
      } catch (e) {
        throw BuiltValueNestedFieldError(
            r'EventUpdate', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
