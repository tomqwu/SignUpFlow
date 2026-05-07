import 'package:flutter/material.dart';

import 'package:signupflow_mobile/shared/widgets/stub_screen.dart';

class CompareScreen extends StatelessWidget {
  const CompareScreen({super.key});

  @override
  Widget build(BuildContext context) => const StubScreen(
        title: 'Compare',
        endpoint: 'GET /solutions/{a}/compare/{b}',
        willLandIn: 'PR 7.10',
      );
}
