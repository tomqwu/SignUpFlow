import 'package:flutter/material.dart';

import 'package:signupflow_mobile/shared/widgets/stub_screen.dart';

class SolverScreen extends StatelessWidget {
  const SolverScreen({super.key});

  @override
  Widget build(BuildContext context) => const StubScreen(
        title: 'Run Solver',
        endpoint: 'POST /solver/solve',
        willLandIn: 'PR 7.9',
      );
}
