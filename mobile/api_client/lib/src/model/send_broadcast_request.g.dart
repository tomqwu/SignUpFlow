// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'send_broadcast_request.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

class _$SendBroadcastRequest extends SendBroadcastRequest {
  @override
  final bool? isUrgent;
  @override
  final String messageText;
  @override
  final BuiltList<int> recipientIds;

  factory _$SendBroadcastRequest(
          [void Function(SendBroadcastRequestBuilder)? updates]) =>
      (SendBroadcastRequestBuilder()..update(updates))._build();

  _$SendBroadcastRequest._(
      {this.isUrgent, required this.messageText, required this.recipientIds})
      : super._();
  @override
  SendBroadcastRequest rebuild(
          void Function(SendBroadcastRequestBuilder) updates) =>
      (toBuilder()..update(updates)).build();

  @override
  SendBroadcastRequestBuilder toBuilder() =>
      SendBroadcastRequestBuilder()..replace(this);

  @override
  bool operator ==(Object other) {
    if (identical(other, this)) return true;
    return other is SendBroadcastRequest &&
        isUrgent == other.isUrgent &&
        messageText == other.messageText &&
        recipientIds == other.recipientIds;
  }

  @override
  int get hashCode {
    var _$hash = 0;
    _$hash = $jc(_$hash, isUrgent.hashCode);
    _$hash = $jc(_$hash, messageText.hashCode);
    _$hash = $jc(_$hash, recipientIds.hashCode);
    _$hash = $jf(_$hash);
    return _$hash;
  }

  @override
  String toString() {
    return (newBuiltValueToStringHelper(r'SendBroadcastRequest')
          ..add('isUrgent', isUrgent)
          ..add('messageText', messageText)
          ..add('recipientIds', recipientIds))
        .toString();
  }
}

class SendBroadcastRequestBuilder
    implements Builder<SendBroadcastRequest, SendBroadcastRequestBuilder> {
  _$SendBroadcastRequest? _$v;

  bool? _isUrgent;
  bool? get isUrgent => _$this._isUrgent;
  set isUrgent(bool? isUrgent) => _$this._isUrgent = isUrgent;

  String? _messageText;
  String? get messageText => _$this._messageText;
  set messageText(String? messageText) => _$this._messageText = messageText;

  ListBuilder<int>? _recipientIds;
  ListBuilder<int> get recipientIds =>
      _$this._recipientIds ??= ListBuilder<int>();
  set recipientIds(ListBuilder<int>? recipientIds) =>
      _$this._recipientIds = recipientIds;

  SendBroadcastRequestBuilder() {
    SendBroadcastRequest._defaults(this);
  }

  SendBroadcastRequestBuilder get _$this {
    final $v = _$v;
    if ($v != null) {
      _isUrgent = $v.isUrgent;
      _messageText = $v.messageText;
      _recipientIds = $v.recipientIds.toBuilder();
      _$v = null;
    }
    return this;
  }

  @override
  void replace(SendBroadcastRequest other) {
    _$v = other as _$SendBroadcastRequest;
  }

  @override
  void update(void Function(SendBroadcastRequestBuilder)? updates) {
    if (updates != null) updates(this);
  }

  @override
  SendBroadcastRequest build() => _build();

  _$SendBroadcastRequest _build() {
    _$SendBroadcastRequest _$result;
    try {
      _$result = _$v ??
          _$SendBroadcastRequest._(
            isUrgent: isUrgent,
            messageText: BuiltValueNullFieldError.checkNotNull(
                messageText, r'SendBroadcastRequest', 'messageText'),
            recipientIds: recipientIds.build(),
          );
    } catch (_) {
      late String _$failedField;
      try {
        _$failedField = 'recipientIds';
        recipientIds.build();
      } catch (e) {
        throw BuiltValueNestedFieldError(
            r'SendBroadcastRequest', _$failedField, e.toString());
      }
      rethrow;
    }
    replace(_$result);
    return _$result;
  }
}

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
