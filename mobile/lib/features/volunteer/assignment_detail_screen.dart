import 'package:flutter/material.dart';

import 'package:signupflow_mobile/shared/widgets/stub_screen.dart';

class AssignmentDetailScreen extends StatelessWidget {
  const AssignmentDetailScreen({required this.assignmentId, super.key});
  final String assignmentId;

  @override
  Widget build(BuildContext context) => StubScreen(
        title: 'Assignment',
        endpoint: 'GET /assignments/$assignmentId · POST /assignments/$assignmentId/{accept,decline}',
        willLandIn: 'PR 7.4',
      );
}
