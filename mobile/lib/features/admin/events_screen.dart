import 'package:flutter/material.dart';

import 'package:signupflow_mobile/shared/widgets/stub_screen.dart';

class EventsScreen extends StatelessWidget {
  const EventsScreen({super.key});

  @override
  Widget build(BuildContext context) => const StubScreen(
        title: 'Events',
        endpoint: 'GET /events · GET /recurring_events',
        willLandIn: 'PR 7.8',
      );
}
