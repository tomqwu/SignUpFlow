import 'package:flutter/material.dart';

import 'package:signupflow_mobile/shared/widgets/stub_screen.dart';

class InboxScreen extends StatelessWidget {
  const InboxScreen({super.key});

  @override
  Widget build(BuildContext context) => const StubScreen(
        title: 'Inbox',
        endpoint: 'no /notifications endpoint yet — DEFERRED FROM MVP',
        willLandIn: 'TBD (backend decision)',
      );
}
