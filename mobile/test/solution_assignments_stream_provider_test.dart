// Sprint 10 PR 10.4b — SSE consumer unit tests.
//
// Pins the parser + provider contract: each `data:` frame surfaces as
// an AssignmentChangedEvent; missing or 401-responses go to the error
// state; the http.Client is closed on provider dispose.

import 'dart:async';
import 'dart:convert';

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:signupflow_mobile/auth/secure_token_storage.dart';
import 'package:signupflow_mobile/features/admin/solution_assignments_stream_provider.dart';

class _FakeHttpClient extends http.BaseClient {
  _FakeHttpClient({required this.respond});

  final Future<http.StreamedResponse> Function(http.BaseRequest req) respond;
  int closeCount = 0;
  http.BaseRequest? lastRequest;

  @override
  Future<http.StreamedResponse> send(http.BaseRequest request) {
    lastRequest = request;
    return respond(request);
  }

  @override
  void close() {
    closeCount++;
    super.close();
  }
}

Stream<List<int>> _sseFramesFor(List<Map<String, Object?>> events) async* {
  for (final ev in events) {
    yield utf8.encode('data: ${jsonEncode(ev)}\n\n');
  }
}

ProviderContainer _container({
  required SecureTokenStorage storage,
  required _FakeHttpClient fakeClient,
}) {
  return ProviderContainer(
    overrides: [
      secureTokenStorageProvider.overrideWithValue(storage),
      sseHttpClientFactoryProvider.overrideWithValue(() => fakeClient),
    ],
  );
}

void main() {
  test('emits one AssignmentChangedEvent per SSE data frame', () async {
    final storage = InMemoryTokenStorage();
    await storage.writeToken('access-jwt');

    final fake = _FakeHttpClient(
      respond: (_) async => http.StreamedResponse(
        _sseFramesFor([
          {
            'type': 'assignment.changed',
            'assignment_id': 1,
            'solution_id': 42,
            'status': 'confirmed',
          },
          {
            'type': 'assignment.changed',
            'assignment_id': 2,
            'solution_id': 42,
            'status': 'declined',
          },
        ]),
        200,
        headers: {'content-type': 'text/event-stream'},
      ),
    );

    final container = _container(storage: storage, fakeClient: fake);
    addTearDown(container.dispose);

    final stream = container.read(solutionAssignmentsStreamProvider(42).stream);
    final events = await stream.take(2).toList();

    expect(events, hasLength(2));
    expect(
      events[0],
      const AssignmentChangedEvent(
        type: 'assignment.changed',
        assignmentId: 1,
        solutionId: 42,
        status: 'confirmed',
      ),
    );
    expect(
      events[1],
      const AssignmentChangedEvent(
        type: 'assignment.changed',
        assignmentId: 2,
        solutionId: 42,
        status: 'declined',
      ),
    );
    expect(fake.lastRequest!.headers['Authorization'], 'Bearer access-jwt');
    expect(fake.lastRequest!.headers['Accept'], 'text/event-stream');
  });

  test('surfaces error when no access token available', () async {
    final storage = InMemoryTokenStorage();
    // no writeToken — readToken returns null
    final fake = _FakeHttpClient(
      respond: (_) async => http.StreamedResponse(const Stream.empty(), 200),
    );
    final container = _container(storage: storage, fakeClient: fake);
    addTearDown(container.dispose);

    expect(
      container.read(solutionAssignmentsStreamProvider(7).stream),
      emitsError(isA<StateError>()),
    );
  });

  test('surfaces error when SSE endpoint returns non-200', () async {
    final storage = InMemoryTokenStorage();
    await storage.writeToken('access-jwt');
    final fake = _FakeHttpClient(
      respond: (_) async => http.StreamedResponse(const Stream.empty(), 401),
    );
    final container = _container(storage: storage, fakeClient: fake);
    addTearDown(container.dispose);

    expect(
      container.read(solutionAssignmentsStreamProvider(7).stream),
      emitsError(isA<http.ClientException>()),
    );
  });

  test('closes the http client on provider dispose', () async {
    final storage = InMemoryTokenStorage();
    await storage.writeToken('access-jwt');
    final fake = _FakeHttpClient(
      respond: (_) async => http.StreamedResponse(
        _sseFramesFor([
          {
            'type': 'assignment.changed',
            'assignment_id': 1,
            'solution_id': 99,
            'status': 'confirmed',
          },
        ]),
        200,
        headers: {'content-type': 'text/event-stream'},
      ),
    );
    final container = _container(storage: storage, fakeClient: fake);
    final stream = container.read(solutionAssignmentsStreamProvider(99).stream);
    // Drain so the connect path runs.
    await stream.first;
    container.dispose();

    expect(fake.closeCount, greaterThanOrEqualTo(1));
  });
}
