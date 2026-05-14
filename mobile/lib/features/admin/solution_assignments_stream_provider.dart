// Sprint 10 PR 10.4b — mobile SSE consumer for Solution Review live refresh.
//
// Subscribes to GET /api/v1/solutions/{id}/assignments/stream and yields one
// AssignmentChangedEvent per `data:` frame. The screen treats each emission
// as a refetch signal (it re-invalidates solutionAssignmentsProvider), so the
// payload only carries enough info to identify which solution changed — the
// canonical list is fetched via the existing non-stream endpoint.
//
// Uses a separate http.Client (not the app's dio) because the dio refresh
// interceptor in api_client.dart awaits responses and would replay-on-401
// mid-stream, breaking SSE.

import 'dart:async';
import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:http/http.dart' as http;
import 'package:signupflow_mobile/api/api_client.dart' show defaultApiBaseUrl;
import 'package:signupflow_mobile/auth/secure_token_storage.dart';

/// SSE payload from the assignments stream. Minimal on purpose — the
/// consumer's job is to refetch, not to merge.
@immutable
class AssignmentChangedEvent {
  const AssignmentChangedEvent({
    required this.type,
    required this.assignmentId,
    required this.solutionId,
    required this.status,
  });

  factory AssignmentChangedEvent.fromJson(Map<String, dynamic> json) {
    return AssignmentChangedEvent(
      type: json['type'] as String,
      assignmentId: json['assignment_id'] as int,
      solutionId: json['solution_id'] as int,
      status: json['status'] as String,
    );
  }

  final String type;
  final int assignmentId;
  final int solutionId;
  final String status;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is AssignmentChangedEvent &&
          other.type == type &&
          other.assignmentId == assignmentId &&
          other.solutionId == solutionId &&
          other.status == status;

  @override
  int get hashCode => Object.hash(type, assignmentId, solutionId, status);
}

/// Factory hook so tests can swap in a fake http.Client returning a canned
/// StreamedResponse.
typedef SseClientFactory = http.Client Function();
final sseHttpClientFactoryProvider = Provider<SseClientFactory>(
  (_) => http.Client.new,
);

final solutionAssignmentsStreamProvider =
    StreamProvider.family<AssignmentChangedEvent, int>((ref, solutionId) {
  final storage = ref.read(secureTokenStorageProvider);
  final client = ref.read(sseHttpClientFactoryProvider)();
  ref.onDispose(client.close);
  return _streamSolutionAssignments(
    client: client,
    storage: storage,
    solutionId: solutionId,
  );
});

Stream<AssignmentChangedEvent> _streamSolutionAssignments({
  required http.Client client,
  required SecureTokenStorage storage,
  required int solutionId,
}) async* {
  final token = await storage.readToken();
  if (token == null || token.isEmpty) {
    throw StateError('No access token available for SSE stream');
  }
  final uri = Uri.parse(
    '$defaultApiBaseUrl/api/v1/solutions/$solutionId/assignments/stream',
  );
  final request = http.Request('GET', uri)
    ..headers['Authorization'] = 'Bearer $token'
    ..headers['Accept'] = 'text/event-stream';

  final response = await client.send(request);
  if (response.statusCode != 200) {
    throw http.ClientException(
      'SSE stream returned ${response.statusCode}',
      uri,
    );
  }

  // W3C SSE format: each event is one-or-more `field: value` lines
  // followed by a blank line. We only care about `data:` lines, which
  // for our payloads always contain a single JSON object on one line.
  final buffer = StringBuffer();
  await for (final line in response.stream
      .transform(utf8.decoder)
      .transform(const LineSplitter())) {
    if (line.isEmpty) {
      final raw = buffer.toString();
      buffer.clear();
      if (raw.isEmpty) continue;
      final decoded = jsonDecode(raw) as Map<String, dynamic>;
      yield AssignmentChangedEvent.fromJson(decoded);
    } else if (line.startsWith('data:')) {
      if (buffer.isNotEmpty) buffer.write('\n');
      buffer.write(line.substring(5).trimLeft());
    }
    // Other field types (`event:`, `id:`, `retry:`, `:` comment) are
    // ignored — the backend only emits `data:` frames.
  }
}
