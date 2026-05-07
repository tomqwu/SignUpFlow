import 'package:flutter/material.dart';

import 'package:signupflow_mobile/shared/widgets/stub_screen.dart';

class SolutionReviewScreen extends StatelessWidget {
  const SolutionReviewScreen({required this.solutionId, super.key});
  final String solutionId;

  @override
  Widget build(BuildContext context) => StubScreen(
        title: 'Solution #$solutionId',
        endpoint: 'GET /solutions/$solutionId · /assignments · /stats',
        willLandIn: 'PR 7.9',
      );
}
