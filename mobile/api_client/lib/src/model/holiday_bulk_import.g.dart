// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'holiday_bulk_import.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$HolidayBulkImport extends HolidayBulkImport {
  @override
  final BuiltList<HolidayBulkImportItem> items;

  factory _$HolidayBulkImport(
          [void Function(HolidayBulkImportBuilder)? updates]) =>
      (HolidayBulkImportBuilder()..update(updates))._build();

  _$HolidayBulkImport._({required this.items}) : super._();
  @override
  HolidayBulkImport rebuild(void Function(HolidayBulkImportBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  HolidayBulkImportBuilder toBuilder() =>
      HolidayBulkImportBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is HolidayBulkImport && items == other.items;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, items.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'HolidayBulkImport')
          ..add('items', items))
        .toString();
  }
}

class HolidayBulkImportBuilder
    implements Builder<HolidayBulkImport, HolidayBulkImportBuilder> {
  _$HolidayBulkImport? _$v;

  ListBuilder<HolidayBulkImportItem>? _items;
  ListBuilder<HolidayBulkImportItem> get items =>
      _$this._items ??= ListBuilder<HolidayBulkImportItem>();
  set items(ListBuilder<HolidayBulkImportItem>? items) => _$this._items = items;

  HolidayBulkImportBuilder() {
    HolidayBulkImport._defaults(this);
  }

  HolidayBulkImportBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _items = $v.items.toBuilder();
      _$v = null;
    }
    return this;
  }

  @override
  void replace(HolidayBulkImport other) {
    _$v = other as _$HolidayBulkImport;
  }

  @override
  void update(void Function(HolidayBulkImportBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  HolidayBulkImport build() => _build();

  _$HolidayBulkImport _build() {
    _$HolidayBulkImport _$result;
    try {
      _$result = _$v ??
          _$HolidayBulkImport._(
            items: items.build(),
          );
    } catch (_) {
      late String _$failedField;
      try {
        _$failedField = 'items';
        items.build();
      } catch (e) {
        throw BuiltValueNestedFieldError(
            r'HolidayBulkImport', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
