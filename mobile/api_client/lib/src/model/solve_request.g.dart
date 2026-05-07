// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'solve_request.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$SolveRequest extends SolveRequest {
  @override
  final bool? changeMin;
  @override
  final Date fromDate;
  @override
  final String? mode;
  @override
  final String orgId;
  @override
  final Date toDate;

  factory _$SolveRequest([void Function(SolveRequestBuilder)? updates]) =>
      (SolveRequestBuilder()..update(updates))._build();

  _$SolveRequest._(
      {this.changeMin,
      required this.fromDate,
      this.mode,
      required this.orgId,
      required this.toDate})
      : super._();
  @override
  SolveRequest rebuild(void Function(SolveRequestBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  SolveRequestBuilder toBuilder() => SolveRequestBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is SolveRequest &&
        changeMin == other.changeMin &&
        fromDate == other.fromDate &&
        mode == other.mode &&
        orgId == other.orgId &&
        toDate == other.toDate;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, changeMin.hashCode);
    _$hash = $jc(_$hash, fromDate.hashCode);
    _$hash = $jc(_$hash, mode.hashCode);
    _$hash = $jc(_$hash, orgId.hashCode);
    _$hash = $jc(_$hash, toDate.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'SolveRequest')
          ..add('changeMin', changeMin)
          ..add('fromDate', fromDate)
          ..add('mode', mode)
          ..add('orgId', orgId)
          ..add('toDate', toDate))
        .toString();
  }
}

class SolveRequestBuilder
    implements Builder<SolveRequest, SolveRequestBuilder> {
  _$SolveRequest? _$v;

  bool? _changeMin;
  bool? get changeMin => _$this._changeMin;
  set changeMin(bool? changeMin) => _$this._changeMin = changeMin;

  Date? _fromDate;
  Date? get fromDate => _$this._fromDate;
  set fromDate(Date? fromDate) => _$this._fromDate = fromDate;

  String? _mode;
  String? get mode => _$this._mode;
  set mode(String? mode) => _$this._mode = mode;

  String? _orgId;
  String? get orgId => _$this._orgId;
  set orgId(String? orgId) => _$this._orgId = orgId;

  Date? _toDate;
  Date? get toDate => _$this._toDate;
  set toDate(Date? toDate) => _$this._toDate = toDate;

  SolveRequestBuilder() {
    SolveRequest._defaults(this);
  }

  SolveRequestBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _changeMin = $v.changeMin;
      _fromDate = $v.fromDate;
      _mode = $v.mode;
      _orgId = $v.orgId;
      _toDate = $v.toDate;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(SolveRequest other) {
    _$v = other as _$SolveRequest;
  }

  @override
  void update(void Function(SolveRequestBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  SolveRequest build() => _build();

  _$SolveRequest _build() {
    final _$result = _$v ??
        _$SolveRequest._(
          changeMin: changeMin,
          fromDate: BuiltValueNullFieldError.checkNotNull(
              fromDate, r'SolveRequest', 'fromDate'),
          mode: mode,
          orgId: BuiltValueNullFieldError.checkNotNull(
              orgId, r'SolveRequest', 'orgId'),
          toDate: BuiltValueNullFieldError.checkNotNull(
              toDate, r'SolveRequest', 'toDate'),
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
