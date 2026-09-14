// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'trial_request.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$TrialRequest extends TrialRequest {
  @override
  final String? billingCycle;
  @override
  final String orgId;
  @override
  final String planTier;
  @override
  final int? trialDays;

  factory _$TrialRequest([void Function(TrialRequestBuilder)? updates]) =>
      (TrialRequestBuilder()..update(updates))._build();

  _$TrialRequest._(
      {this.billingCycle,
      required this.orgId,
      required this.planTier,
      this.trialDays})
      : super._();
  @override
  TrialRequest rebuild(void Function(TrialRequestBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  TrialRequestBuilder toBuilder() => TrialRequestBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is TrialRequest &&
        billingCycle == other.billingCycle &&
        orgId == other.orgId &&
        planTier == other.planTier &&
        trialDays == other.trialDays;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, billingCycle.hashCode);
    _$hash = $jc(_$hash, orgId.hashCode);
    _$hash = $jc(_$hash, planTier.hashCode);
    _$hash = $jc(_$hash, trialDays.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'TrialRequest')
          ..add('billingCycle', billingCycle)
          ..add('orgId', orgId)
          ..add('planTier', planTier)
          ..add('trialDays', trialDays))
        .toString();
  }
}

class TrialRequestBuilder
    implements Builder<TrialRequest, TrialRequestBuilder> {
  _$TrialRequest? _$v;

  String? _billingCycle;
  String? get billingCycle => _$this._billingCycle;
  set billingCycle(String? billingCycle) => _$this._billingCycle = billingCycle;

  String? _orgId;
  String? get orgId => _$this._orgId;
  set orgId(String? orgId) => _$this._orgId = orgId;

  String? _planTier;
  String? get planTier => _$this._planTier;
  set planTier(String? planTier) => _$this._planTier = planTier;

  int? _trialDays;
  int? get trialDays => _$this._trialDays;
  set trialDays(int? trialDays) => _$this._trialDays = trialDays;

  TrialRequestBuilder() {
    TrialRequest._defaults(this);
  }

  TrialRequestBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _billingCycle = $v.billingCycle;
      _orgId = $v.orgId;
      _planTier = $v.planTier;
      _trialDays = $v.trialDays;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(TrialRequest other) {
    _$v = other as _$TrialRequest;
  }

  @override
  void update(void Function(TrialRequestBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  TrialRequest build() => _build();

  _$TrialRequest _build() {
    final _$result = _$v ??
        _$TrialRequest._(
          billingCycle: billingCycle,
          orgId: BuiltValueNullFieldError.checkNotNull(
              orgId, r'TrialRequest', 'orgId'),
          planTier: BuiltValueNullFieldError.checkNotNull(
              planTier, r'TrialRequest', 'planTier'),
          trialDays: trialDays,
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
