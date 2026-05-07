import 'package:flutter/material.dart';

import 'package:signupflow_mobile/shared/widgets/stub_screen.dart';

class PublishScreen extends StatelessWidget {
  const PublishScreen({super.key});

  @override
  Widget build(BuildContext context) => const StubScreen(
        title: 'Publish',
        endpoint: 'POST /solutions/{id}/{publish,unpublish,rollback}',
        willLandIn: 'PR 7.10',
      );
}
