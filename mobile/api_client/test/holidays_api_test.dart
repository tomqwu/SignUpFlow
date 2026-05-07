import 'package:test/test.dart';
import 'package:signupflow_api/signupflow_api.dart';


/// tests for HolidaysApi
void main() {
  final instance = SignupflowApi().getHolidaysApi();

  group(HolidaysApi, () {
    // Bulk Import Holidays
    //
    // Admin-only bulk-create holidays for one org.  Common pattern for importing a full year's federal/diocesan calendar in one request. Skips dates that already have a holiday row in the target org; returns those as errors so the caller can decide whether to retry.
    //
    //Future<HolidayBulkImportResponse> bulkImportHolidays(String orgId, HolidayBulkImport holidayBulkImport) async
    test('test bulkImportHolidays', () async {
      // TODO
    });

    // Create Holiday
    //
    // Create a single holiday (admin only).
    //
    //Future<HolidayResponse> createHoliday(HolidayCreate holidayCreate) async
    test('test createHoliday', () async {
      // TODO
    });

    // Delete Holiday
    //
    //Future deleteHoliday(int holidayId) async
    test('test deleteHoliday', () async {
      // TODO
    });

    // Get Holiday
    //
    //Future<HolidayResponse> getHoliday(int holidayId) async
    test('test getHoliday', () async {
      // TODO
    });

    // List Holidays
    //
    // List holidays for one org. Caller must be a member.
    //
    //Future<ListResponseHolidayResponse> listHolidays(String orgId, { int limit, int offset }) async
    test('test listHolidays', () async {
      // TODO
    });

    // Update Holiday
    //
    //Future<HolidayResponse> updateHoliday(int holidayId, HolidayUpdate holidayUpdate) async
    test('test updateHoliday', () async {
      // TODO
    });

  });
}
