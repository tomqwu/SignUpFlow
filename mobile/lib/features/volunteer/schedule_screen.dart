import 'package:flutter/material.dart';

import 'package:signupflow_mobile/shared/widgets/stub_screen.dart';

class VolunteerScheduleScreen extends StatelessWidget {
  const VolunteerScheduleScreen({super.key});

  @override
  Widget build(BuildContext context) => const StubScreen(
        title: 'Schedule',
        endpoint: 'GET /people/me/assignments',
        willLandIn: 'PR 7.3',
      );
}
