// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'conflict_check_request.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$ConflictCheckRequest extends ConflictCheckRequest {
  @override
  final String eventId;
  @override
  final String personId;

  factory _$ConflictCheckRequest(
          [void Function(ConflictCheckRequestBuilder)? updates]) =>
      (ConflictCheckRequestBuilder()..update(updates))._build();

  _$ConflictCheckRequest._({required this.eventId, required this.personId})
      : super._();
  @override
  ConflictCheckRequest rebuild(
          void Function(ConflictCheckRequestBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  ConflictCheckRequestBuilder toBuilder() =>
      ConflictCheckRequestBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is ConflictCheckRequest &&
        eventId == other.eventId &&
        personId == other.personId;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, eventId.hashCode);
    _$hash = $jc(_$hash, personId.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'ConflictCheckRequest')
          ..add('eventId', eventId)
          ..add('personId', personId))
        .toString();
  }
}

class ConflictCheckRequestBuilder
    implements Builder<ConflictCheckRequest, ConflictCheckRequestBuilder> {
  _$ConflictCheckRequest? _$v;

  String? _eventId;
  String? get eventId => _$this._eventId;
  set eventId(String? eventId) => _$this._eventId = eventId;

  String? _personId;
  String? get personId => _$this._personId;
  set personId(String? personId) => _$this._personId = personId;

  ConflictCheckRequestBuilder() {
    ConflictCheckRequest._defaults(this);
  }

  ConflictCheckRequestBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _eventId = $v.eventId;
      _personId = $v.personId;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(ConflictCheckRequest other) {
    _$v = other as _$ConflictCheckRequest;
  }

  @override
  void update(void Function(ConflictCheckRequestBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  ConflictCheckRequest build() => _build();

  _$ConflictCheckRequest _build() {
    final _$result = _$v ??
        _$ConflictCheckRequest._(
          eventId: BuiltValueNullFieldError.checkNotNull(
              eventId, r'ConflictCheckRequest', 'eventId'),
          personId: BuiltValueNullFieldError.checkNotNull(
              personId, r'ConflictCheckRequest', 'personId'),
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
