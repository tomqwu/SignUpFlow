// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'broadcast_response.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$BroadcastResponse extends BroadcastResponse {
  @override
  final int estimatedCostCents;
  @override
  final String message;
  @override
  final int queuedCount;
  @override
  final int skippedCount;
  @override
  final String status;
  @override
  final int totalRecipients;

  factory _$BroadcastResponse(
          [void Function(BroadcastResponseBuilder)? updates]) =>
      (BroadcastResponseBuilder()..update(updates))._build();

  _$BroadcastResponse._(
      {required this.estimatedCostCents,
      required this.message,
      required this.queuedCount,
      required this.skippedCount,
      required this.status,
      required this.totalRecipients})
      : super._();
  @override
  BroadcastResponse rebuild(void Function(BroadcastResponseBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  BroadcastResponseBuilder toBuilder() =>
      BroadcastResponseBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is BroadcastResponse &&
        estimatedCostCents == other.estimatedCostCents &&
        message == other.message &&
        queuedCount == other.queuedCount &&
        skippedCount == other.skippedCount &&
        status == other.status &&
        totalRecipients == other.totalRecipients;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, estimatedCostCents.hashCode);
    _$hash = $jc(_$hash, message.hashCode);
    _$hash = $jc(_$hash, queuedCount.hashCode);
    _$hash = $jc(_$hash, skippedCount.hashCode);
    _$hash = $jc(_$hash, status.hashCode);
    _$hash = $jc(_$hash, totalRecipients.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'BroadcastResponse')
          ..add('estimatedCostCents', estimatedCostCents)
          ..add('message', message)
          ..add('queuedCount', queuedCount)
          ..add('skippedCount', skippedCount)
          ..add('status', status)
          ..add('totalRecipients', totalRecipients))
        .toString();
  }
}

class BroadcastResponseBuilder
    implements Builder<BroadcastResponse, BroadcastResponseBuilder> {
  _$BroadcastResponse? _$v;

  int? _estimatedCostCents;
  int? get estimatedCostCents => _$this._estimatedCostCents;
  set estimatedCostCents(int? estimatedCostCents) =>
      _$this._estimatedCostCents = estimatedCostCents;

  String? _message;
  String? get message => _$this._message;
  set message(String? message) => _$this._message = message;

  int? _queuedCount;
  int? get queuedCount => _$this._queuedCount;
  set queuedCount(int? queuedCount) => _$this._queuedCount = queuedCount;

  int? _skippedCount;
  int? get skippedCount => _$this._skippedCount;
  set skippedCount(int? skippedCount) => _$this._skippedCount = skippedCount;

  String? _status;
  String? get status => _$this._status;
  set status(String? status) => _$this._status = status;

  int? _totalRecipients;
  int? get totalRecipients => _$this._totalRecipients;
  set totalRecipients(int? totalRecipients) =>
      _$this._totalRecipients = totalRecipients;

  BroadcastResponseBuilder() {
    BroadcastResponse._defaults(this);
  }

  BroadcastResponseBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _estimatedCostCents = $v.estimatedCostCents;
      _message = $v.message;
      _queuedCount = $v.queuedCount;
      _skippedCount = $v.skippedCount;
      _status = $v.status;
      _totalRecipients = $v.totalRecipients;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(BroadcastResponse other) {
    _$v = other as _$BroadcastResponse;
  }

  @override
  void update(void Function(BroadcastResponseBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  BroadcastResponse build() => _build();

  _$BroadcastResponse _build() {
    final _$result = _$v ??
        _$BroadcastResponse._(
          estimatedCostCents: BuiltValueNullFieldError.checkNotNull(
              estimatedCostCents, r'BroadcastResponse', 'estimatedCostCents'),
          message: BuiltValueNullFieldError.checkNotNull(
              message, r'BroadcastResponse', 'message'),
          queuedCount: BuiltValueNullFieldError.checkNotNull(
              queuedCount, r'BroadcastResponse', 'queuedCount'),
          skippedCount: BuiltValueNullFieldError.checkNotNull(
              skippedCount, r'BroadcastResponse', 'skippedCount'),
          status: BuiltValueNullFieldError.checkNotNull(
              status, r'BroadcastResponse', 'status'),
          totalRecipients: BuiltValueNullFieldError.checkNotNull(
              totalRecipients, r'BroadcastResponse', 'totalRecipients'),
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
