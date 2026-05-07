// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'export_format.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$ExportFormat extends ExportFormat {
  @override
  final String format;
  @override
  final String? scope;

  factory _$ExportFormat([void Function(ExportFormatBuilder)? updates]) =>
      (ExportFormatBuilder()..update(updates))._build();

  _$ExportFormat._({required this.format, this.scope}) : super._();
  @override
  ExportFormat rebuild(void Function(ExportFormatBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  ExportFormatBuilder toBuilder() => ExportFormatBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is ExportFormat &&
        format == other.format &&
        scope == other.scope;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, format.hashCode);
    _$hash = $jc(_$hash, scope.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'ExportFormat')
          ..add('format', format)
          ..add('scope', scope))
        .toString();
  }
}

class ExportFormatBuilder
    implements Builder<ExportFormat, ExportFormatBuilder> {
  _$ExportFormat? _$v;

  String? _format;
  String? get format => _$this._format;
  set format(String? format) => _$this._format = format;

  String? _scope;
  String? get scope => _$this._scope;
  set scope(String? scope) => _$this._scope = scope;

  ExportFormatBuilder() {
    ExportFormat._defaults(this);
  }

  ExportFormatBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _format = $v.format;
      _scope = $v.scope;
      _$v = null;
    }
    return this;
  }

  @override
  void replace(ExportFormat other) {
    _$v = other as _$ExportFormat;
  }

  @override
  void update(void Function(ExportFormatBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  ExportFormat build() => _build();

  _$ExportFormat _build() {
    final _$result = _$v ??
        _$ExportFormat._(
          format: BuiltValueNullFieldError.checkNotNull(
              format, r'ExportFormat', 'format'),
          scope: scope,
        );
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
