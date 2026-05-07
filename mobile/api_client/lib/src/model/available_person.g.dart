// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'available_person.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$AvailablePerson extends AvailablePerson {
  @override
  final String? email;
  @override
  final String id;
  @override
  final bool isAssigned;
  @override
  final bool? isBlocked;
  @override
  final String name;
  @override
  final BuiltList<String> roles;

  factory _$AvailablePerson([void Function(AvailablePersonBuilder)? updates]) =>
      (AvailablePersonBuilder()..update(updates))._build();

  _$AvailablePerson._(
      {this.email,
      required this.id,
      required this.isAssigned,
      this.isBlocked,
      required this.name,
      required this.roles})
      : super._();
  @override
  AvailablePerson rebuild(void Function(AvailablePersonBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  AvailablePersonBuilder toBuilder() => AvailablePersonBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is AvailablePerson &&
        email == other.email &&
        id == other.id &&
        isAssigned == other.isAssigned &&
        isBlocked == other.isBlocked &&
        name == other.name &&
        roles == other.roles;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, email.hashCode);
    _$hash = $jc(_$hash, id.hashCode);
    _$hash = $jc(_$hash, isAssigned.hashCode);
    _$hash = $jc(_$hash, isBlocked.hashCode);
    _$hash = $jc(_$hash, name.hashCode);
    _$hash = $jc(_$hash, roles.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'AvailablePerson')
          ..add('email', email)
          ..add('id', id)
          ..add('isAssigned', isAssigned)
          ..add('isBlocked', isBlocked)
          ..add('name', name)
          ..add('roles', roles))
        .toString();
  }
}

class AvailablePersonBuilder
    implements Builder<AvailablePerson, AvailablePersonBuilder> {
  _$AvailablePerson? _$v;

  String? _email;
  String? get email => _$this._email;
  set email(String? email) => _$this._email = email;

  String? _id;
  String? get id => _$this._id;
  set id(String? id) => _$this._id = id;

  bool? _isAssigned;
  bool? get isAssigned => _$this._isAssigned;
  set isAssigned(bool? isAssigned) => _$this._isAssigned = isAssigned;

  bool? _isBlocked;
  bool? get isBlocked => _$this._isBlocked;
  set isBlocked(bool? isBlocked) => _$this._isBlocked = isBlocked;

  String? _name;
  String? get name => _$this._name;
  set name(String? name) => _$this._name = name;

  ListBuilder<String>? _roles;
  ListBuilder<String> get roles => _$this._roles ??= ListBuilder<String>();
  set roles(ListBuilder<String>? roles) => _$this._roles = roles;

  AvailablePersonBuilder() {
    AvailablePerson._defaults(this);
  }

  AvailablePersonBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _email = $v.email;
      _id = $v.id;
      _isAssigned = $v.isAssigned;
      _isBlocked = $v.isBlocked;
      _name = $v.name;
      _roles = $v.roles.toBuilder();
      _$v = null;
    }
    return this;
  }

  @override
  void replace(AvailablePerson other) {
    _$v = other as _$AvailablePerson;
  }

  @override
  void update(void Function(AvailablePersonBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  AvailablePerson build() => _build();

  _$AvailablePerson _build() {
    _$AvailablePerson _$result;
    try {
      _$result = _$v ??
          _$AvailablePerson._(
            email: email,
            id: BuiltValueNullFieldError.checkNotNull(
                id, r'AvailablePerson', 'id'),
            isAssigned: BuiltValueNullFieldError.checkNotNull(
                isAssigned, r'AvailablePerson', 'isAssigned'),
            isBlocked: isBlocked,
            name: BuiltValueNullFieldError.checkNotNull(
                name, r'AvailablePerson', 'name'),
            roles: roles.build(),
          );
    } catch (_) {
      late String _$failedField;
      try {
        _$failedField = 'roles';
        roles.build();
      } catch (e) {
        throw BuiltValueNestedFieldError(
            r'AvailablePerson', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
