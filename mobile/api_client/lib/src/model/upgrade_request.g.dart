// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'upgrade_request.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$UpgradeRequest extends UpgradeRequest {
  @override
  final String billingCycle;
  @override
  final String orgId;
  @override
  final String? paymentMethodId;
  @override
  final String planTier;
  @override
  final int? trialDays;

  factory _$UpgradeRequest([void Function(UpgradeRequestBuilder)? updates]) =>
      (UpgradeRequestBuilder()..update(updates))._build();

  _$UpgradeRequest._(
      {required this.billingCycle,
      required this.orgId,
      this.paymentMethodId,
      required this.planTier,
      this.trialDays})
      : super._();
  @override
  UpgradeRequest rebuild(void Function(UpgradeRequestBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  UpgradeRequestBuilder toBuilder() => UpgradeRequestBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is UpgradeRequest &&
        billingCycle == other.billingCycle &&
        orgId == other.orgId &&
        paymentMethodId == other.paymentMethodId &&
        planTier == other.planTier &&
        trialDays == other.trialDays;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, billingCycle.hashCode);
    _$hash = $jc(_$hash, orgId.hashCode);
    _$hash = $jc(_$hash, paymentMethodId.hashCode);
    _$hash = $jc(_$hash, planTier.hashCode);
    _$hash = $jc(_$hash, trialDays.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'UpgradeRequest')
          ..add('billingCycle', billingCycle)
          ..add('orgId', orgId)
          ..add('paymentMethodId', paymentMethodId)
          ..add('planTier', planTier)
          ..add('trialDays', trialDays))
        .toString();
  }
}

class UpgradeRequestBuilder
    implements Builder<UpgradeRequest, UpgradeRequestBuilder> {
  _$UpgradeRequest? _$v;

  String? _billingCycle;
  String? get billingCycle => _$this._billingCycle;
  set billingCycle(String? billingCycle) => _$this._billingCycle = billingCycle;

  String? _orgId;
  String? get orgId => _$this._orgId;
  set orgId(String? orgId) => _$this._orgId = orgId;

  String? _paymentMethodId;
  String? get paymentMethodId => _$this._paymentMethodId;
  set paymentMethodId(String? paymentMethodId) =>
      _$this._paymentMethodId = paymentMethodId;

  String? _planTier;
  String? get planTier => _$this._planTier;
  set planTier(String? planTier) => _$this._planTier = planTier;

  int? _trialDays;
  int? get trialDays => _$this._trialDays;
  set trialDays(int? trialDays) => _$this._trialDays = trialDays;

  UpgradeRequestBuilder() {
    UpgradeRequest._defaults(this);
  }

  UpgradeRequestBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _billingCycle = $v.billingCycle;
      _orgId = $v.orgId;
      _paymentMethodId = $v.paymentMethodId;
      _planTier = $v.planTier;
      _trialDays = $v.trialDays;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(UpgradeRequest other) {
    _$v = other as _$UpgradeRequest;
  }

  @override
  void update(void Function(UpgradeRequestBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  UpgradeRequest build() => _build();

  _$UpgradeRequest _build() {
    final _$result = _$v ??
        _$UpgradeRequest._(
          billingCycle: BuiltValueNullFieldError.checkNotNull(
              billingCycle, r'UpgradeRequest', 'billingCycle'),
          orgId: BuiltValueNullFieldError.checkNotNull(
              orgId, r'UpgradeRequest', 'orgId'),
          paymentMethodId: paymentMethodId,
          planTier: BuiltValueNullFieldError.checkNotNull(
              planTier, r'UpgradeRequest', 'planTier'),
          trialDays: trialDays,
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
