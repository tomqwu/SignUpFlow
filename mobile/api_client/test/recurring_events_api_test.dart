import 'package:test/test.dart';
import 'package:signupflow_api/signupflow_api.dart';


/// tests for RecurringEventsApi
void main() {
  final instance = SignupflowApi().getRecurringEventsApi();

  group(RecurringEventsApi, () {
    // Create Recurring Series
    //
    // Create a new recurring event series and generate all occurrences.  Requires admin access. Creates: 1. RecurringSeries template 2. Individual Event occurrences based on pattern 3. Links occurrences to series  Returns the created series with occurrence count.
    //
    //Future<RecurringSeriesResponse> createRecurringSeries(String orgId, RecurringSeriesCreate recurringSeriesCreate) async
    test('test createRecurringSeries', () async {
      // TODO
    });

    // Delete Recurring Series
    //
    // Delete a recurring series and all its occurrences.  Requires admin access. Deletes: 1. All event occurrences linked to series 2. All exceptions for those occurrences 3. The series itself  Warning: This is irreversible!
    //
    //Future<JsonObject> deleteRecurringSeries(String seriesId) async
    test('test deleteRecurringSeries', () async {
      // TODO
    });

    // Get Recurring Series
    //
    // Get a specific recurring series by ID.  Returns series details with occurrence count.
    //
    //Future<RecurringSeriesResponse> getRecurringSeries(String seriesId) async
    test('test getRecurringSeries', () async {
      // TODO
    });

    // Get Series Occurrences
    //
    // Get all event occurrences for a recurring series.  Returns list of Event objects with exception indicators.
    //
    //Future<JsonObject> getSeriesOccurrences(String seriesId) async
    test('test getSeriesOccurrences', () async {
      // TODO
    });

    // List Recurring Series
    //
    // List all recurring series for an organization, scoped to the caller's org.
    //
    //Future<ListResponseRecurringSeriesResponse> listRecurringSeries(String orgId, { bool activeOnly, int limit, int offset }) async
    test('test listRecurringSeries', () async {
      // TODO
    });

    // Preview Occurrences
    //
    // Preview occurrences for a recurring pattern WITHOUT creating them.  Used by the UI calendar preview to show occurrences before saving. Returns up to 100 occurrences for preview.
    //
    //Future<BuiltList<OccurrencePreview>> previewOccurrences(String orgId, PreviewRequest previewRequest) async
    test('test previewOccurrences', () async {
      // TODO
    });

    // Update Series Template
    //
    // Update the series template (affects future occurrences).  Only updates the template - existing occurrences are NOT changed. Use this to modify what future occurrences will look like.  Note: To modify recurrence pattern, delete and recreate the series.
    //
    //Future<JsonObject> updateSeriesTemplate(String seriesId, { String title, String location, BuiltMap<String, JsonObject> requestBody }) async
    test('test updateSeriesTemplate', () async {
      // TODO
    });

  });
}
