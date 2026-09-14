import 'package:test/test.dart';
import 'package:signupflow_api/signupflow_api.dart';

// tests for TrialRequest
void main() {
  final instance = TrialRequestBuilder();
  // TODO add properties to the builder and call build()

  group(TrialRequest, () {
    // Billing cycle after trial
    // String billingCycle (default value: 'monthly')
    test('to test the property `billingCycle`', () async {
      // TODO
    });

    // Organization ID
    // String orgId
    test('to test the property `orgId`', () async {
      // TODO
    });

    // Plan tier to trial (starter, pro, enterprise)
    // String planTier
    test('to test the property `planTier`', () async {
      // TODO
    });

    // Number of trial days
    // int trialDays (default value: 14)
    test('to test the property `trialDays`', () async {
      // TODO
    });

  });
}
