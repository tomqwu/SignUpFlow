// Stub screen — used by all 7.1 placeholder screens. Visual matches the
// page chrome (page title + scroll body + footer note), with a single
// large card explaining what lands in this screen and which future PR
// fills it. Stubs are intentionally light so PR 7.1 doesn't pretend to
// ship features it doesn't have.

import 'package:flutter/material.dart';

import 'package:signupflow_mobile/theme/colors.dart';
import 'package:signupflow_mobile/theme/components.dart';
import 'package:signupflow_mobile/theme/typography.dart';

class StubScreen extends StatelessWidget {
  const StubScreen({
    required this.title,
    required this.endpoint,
    required this.willLandIn,
    this.action,
    super.key,
  });

  final String title;
  final String endpoint;
  final String willLandIn;
  final Widget? action;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            if (action != null)
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 20),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.end,
                  children: [action!],
                ),
              ),
            const SizedBox(height: 4),
            PageTitle(title),
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.fromLTRB(16, 0, 16, 96),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    BlockCard(
                      padding: const EdgeInsets.all(18),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('SPRINT 7.1 STUB', style: BlockType.monoLabel),
                          const SizedBox(height: 8),
                          Text(
                            'Real content lands in $willLandIn.',
                            style: BlockType.body,
                          ),
                          const SizedBox(height: 12),
                          Text('SOURCE ENDPOINT', style: BlockType.monoLabel),
                          const SizedBox(height: 4),
                          Text(
                            endpoint,
                            style: BlockType.monoData
                                .copyWith(color: BlockColors.accentInk),
                          ),
                          const SizedBox(height: 16),
                          Text(
                            'See mobile/prototype/screenshots/v2/ for the visual '
                            'target. The Block-Mono brand is already wired '
                            '(see brand-spec.md) — only the data layer is missing.',
                            style: BlockType.bodySm,
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
