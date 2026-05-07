import 'package:flutter/material.dart';

import 'package:signupflow_mobile/shared/widgets/stub_screen.dart';

class DashboardScreen extends StatelessWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context) => const StubScreen(
        title: 'Dashboard',
        endpoint: 'GET /analytics/org · GET /solutions',
        willLandIn: 'PR 7.7',
      );
}
