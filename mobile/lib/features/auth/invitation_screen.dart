import 'package:flutter/material.dart';

import 'package:signupflow_mobile/shared/widgets/stub_screen.dart';

class InvitationScreen extends StatelessWidget {
  const InvitationScreen({super.key});

  @override
  Widget build(BuildContext context) => const StubScreen(
        title: 'Invitation',
        endpoint: 'GET /invitations/verify · POST /invitations/accept',
        willLandIn: 'PR 7.2 (auth flow)',
      );
}
