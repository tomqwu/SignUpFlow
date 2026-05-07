import 'package:test/test.dart';
import 'package:signupflow_api/signupflow_api.dart';

// tests for ExportFormat
void main() {
  final instance = ExportFormatBuilder();
  // TODO add properties to the builder and call build()

  group(ExportFormat, () {
    // Export format: json, csv, pdf, or ics
    // String format
    test('to test the property `format`', () async {
      // TODO
    });

    // Export scope: org, person:{id}, or team:{id}
    // String scope (default value: 'org')
    test('to test the property `scope`', () async {
      // TODO
    });

  });
}
