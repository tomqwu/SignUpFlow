// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'downgrade_request.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$DowngradeRequest extends DowngradeRequest {
  @override
  final String newPlanTier;
  @override
  final String orgId;
  @override
  final String? reason;

  factory _$DowngradeRequest(
          [void Function(DowngradeRequestBuilder)? updates]) =>
      (DowngradeRequestBuilder()..update(updates))._build();

  _$DowngradeRequest._(
      {required this.newPlanTier, required this.orgId, this.reason})
      : super._();
  @override
  DowngradeRequest rebuild(void Function(DowngradeRequestBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  DowngradeRequestBuilder toBuilder() =>
      DowngradeRequestBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is DowngradeRequest &&
        newPlanTier == other.newPlanTier &&
        orgId == other.orgId &&
        reason == other.reason;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, newPlanTier.hashCode);
    _$hash = $jc(_$hash, orgId.hashCode);
    _$hash = $jc(_$hash, reason.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'DowngradeRequest')
          ..add('newPlanTier', newPlanTier)
          ..add('orgId', orgId)
          ..add('reason', reason))
        .toString();
  }
}

class DowngradeRequestBuilder
    implements Builder<DowngradeRequest, DowngradeRequestBuilder> {
  _$DowngradeRequest? _$v;

  String? _newPlanTier;
  String? get newPlanTier => _$this._newPlanTier;
  set newPlanTier(String? newPlanTier) => _$this._newPlanTier = newPlanTier;

  String? _orgId;
  String? get orgId => _$this._orgId;
  set orgId(String? orgId) => _$this._orgId = orgId;

  String? _reason;
  String? get reason => _$this._reason;
  set reason(String? reason) => _$this._reason = reason;

  DowngradeRequestBuilder() {
    DowngradeRequest._defaults(this);
  }

  DowngradeRequestBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _newPlanTier = $v.newPlanTier;
      _orgId = $v.orgId;
      _reason = $v.reason;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(DowngradeRequest other) {
    _$v = other as _$DowngradeRequest;
  }

  @override
  void update(void Function(DowngradeRequestBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  DowngradeRequest build() => _build();

  _$DowngradeRequest _build() {
    final _$result = _$v ??
        _$DowngradeRequest._(
          newPlanTier: BuiltValueNullFieldError.checkNotNull(
              newPlanTier, r'DowngradeRequest', 'newPlanTier'),
          orgId: BuiltValueNullFieldError.checkNotNull(
              orgId, r'DowngradeRequest', 'orgId'),
          reason: reason,
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
