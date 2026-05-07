import 'package:flutter/material.dart';

import 'package:signupflow_mobile/shared/widgets/stub_screen.dart';

class AvailabilityScreen extends StatelessWidget {
  const AvailabilityScreen({super.key});

  @override
  Widget build(BuildContext context) => const StubScreen(
        title: 'Availability',
        endpoint: 'GET /availability · POST /availability/{exceptions,rrule}',
        willLandIn: 'PR 7.5',
      );
}
