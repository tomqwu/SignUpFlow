import 'package:test/test.dart';
import 'package:signupflow_api/signupflow_api.dart';


/// tests for AuditApi
void main() {
  final instance = SignupflowApi().getAuditApi();

  group(AuditApi, () {
    // List Audit Logs
    //
    // Return audit log rows scoped to the caller's organization.  Admin-only. Each call is itself recorded as a `data.exported` audit event so reads of the audit log are themselves auditable.
    //
    //Future<ListResponseAuditLogResponse> listAuditLogs({ String userId, String action, String resourceType, DateTime startDate, DateTime endDate, String status, int limit, int offset }) async
    test('test listAuditLogs', () async {
      // TODO
    });

  });
}
