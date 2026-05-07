// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'bulk_import_response.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$BulkImportResponse extends BulkImportResponse {
  @override
  final int created;
  @override
  final BuiltList<BulkImportItemError> errors;
  @override
  final int skipped;

  factory _$BulkImportResponse(
          [void Function(BulkImportResponseBuilder)? updates]) =>
      (BulkImportResponseBuilder()..update(updates))._build();

  _$BulkImportResponse._(
      {required this.created, required this.errors, required this.skipped})
      : super._();
  @override
  BulkImportResponse rebuild(
          void Function(BulkImportResponseBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  BulkImportResponseBuilder toBuilder() =>
      BulkImportResponseBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is BulkImportResponse &&
        created == other.created &&
        errors == other.errors &&
        skipped == other.skipped;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, created.hashCode);
    _$hash = $jc(_$hash, errors.hashCode);
    _$hash = $jc(_$hash, skipped.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'BulkImportResponse')
          ..add('created', created)
          ..add('errors', errors)
          ..add('skipped', skipped))
        .toString();
  }
}

class BulkImportResponseBuilder
    implements Builder<BulkImportResponse, BulkImportResponseBuilder> {
  _$BulkImportResponse? _$v;

  int? _created;
  int? get created => _$this._created;
  set created(int? created) => _$this._created = created;

  ListBuilder<BulkImportItemError>? _errors;
  ListBuilder<BulkImportItemError> get errors =>
      _$this._errors ??= ListBuilder<BulkImportItemError>();
  set errors(ListBuilder<BulkImportItemError>? errors) =>
      _$this._errors = errors;

  int? _skipped;
  int? get skipped => _$this._skipped;
  set skipped(int? skipped) => _$this._skipped = skipped;

  BulkImportResponseBuilder() {
    BulkImportResponse._defaults(this);
  }

  BulkImportResponseBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _created = $v.created;
      _errors = $v.errors.toBuilder();
      _skipped = $v.skipped;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(BulkImportResponse other) {
    _$v = other as _$BulkImportResponse;
  }

  @override
  void update(void Function(BulkImportResponseBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  BulkImportResponse build() => _build();

  _$BulkImportResponse _build() {
    _$BulkImportResponse _$result;
    try {
      _$result = _$v ??
          _$BulkImportResponse._(
            created: BuiltValueNullFieldError.checkNotNull(
                created, r'BulkImportResponse', 'created'),
            errors: errors.build(),
            skipped: BuiltValueNullFieldError.checkNotNull(
                skipped, r'BulkImportResponse', 'skipped'),
          );
    } catch (_) {
      late String _$failedField;
      try {
        _$failedField = 'errors';
        errors.build();
      } catch (e) {
        throw BuiltValueNestedFieldError(
            r'BulkImportResponse', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
