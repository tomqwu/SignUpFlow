import 'package:flutter/material.dart';

import 'package:signupflow_mobile/shared/widgets/stub_screen.dart';

class PeopleScreen extends StatelessWidget {
  const PeopleScreen({super.key});

  @override
  Widget build(BuildContext context) => const StubScreen(
        title: 'People',
        endpoint: 'GET /people · POST /invitations',
        willLandIn: 'PR 7.8',
      );
}
