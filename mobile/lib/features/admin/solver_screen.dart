// Admin Solver — Sprint 7.9.
// Visual target: mobile/prototype/screenshots/v2/11-a-solver.png.

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import 'package:signupflow_mobile/features/admin/solver_provider.dart';
import 'package:signupflow_mobile/theme/colors.dart';
import 'package:signupflow_mobile/theme/components.dart';
import 'package:signupflow_mobile/theme/typography.dart';

class SolverScreen extends ConsumerStatefulWidget {
  const SolverScreen({super.key});

  @override
  ConsumerState<SolverScreen> createState() => _SolverScreenState();
}

class _SolverScreenState extends ConsumerState<SolverScreen> {
  late DateTime _from;
  late DateTime _to;
  bool _changeMin = true;
  String _mode = 'strict';

  @override
  void initState() {
    super.initState();
    final today = DateTime.now();
    _from = today;
    _to = today.add(const Duration(days: 28));
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(solverControllerProvider);
    return Scaffold(
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.fromLTRB(16, 4, 16, 96),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const PageTitle('Run Solver'),
              const MonoLabel('Date range'),
              Row(
                children: [
                  Expanded(child: _DateField(label: 'From', value: _from, onTap: () => _pick(true))),
                  const SizedBox(width: 8),
                  Expanded(child: _DateField(label: 'To', value: _to, onTap: () => _pick(false))),
                ],
              ),
              const MonoLabel('Mode'),
              _ModeSegment(
                value: _mode,
                onChanged: (v) => setState(() => _mode = v),
              ),
              const MonoLabel('Options'),
              _OptionRow(
                title: 'Minimize moves from published',
                subtitle: 'Bias the solver toward keeping current published assignments.',
                value: _changeMin,
                onChanged: (v) => setState(() => _changeMin = v),
              ),
              const SizedBox(height: 16),
              BlockButton(
                label: state.busy ? 'Solving…' : 'Run solver →',
                kind: BlockButtonKind.go,
                onPressed: state.busy
                    ? null
                    : () async {
                        final id = await ref.read(solverControllerProvider.notifier).run(
                              fromDate: _from,
                              toDate: _to,
                              changeMin: _changeMin,
                              mode: _mode,
                            );
                        if (!context.mounted) return;
                        if (id != null) {
                          GoRouter.of(context).go('/a/solution/$id');
                        } else {
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(content: Text('Solve failed: ${state.lastError ?? "unknown"}')),
                          );
                        }
                      },
              ),
              if (state.lastSolutionId != null) ...[
                const MonoLabel('Last solve'),
                BlockCard(
                  child: Row(
                    children: [
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text('Solution #${state.lastSolutionId}', style: BlockType.subhead),
                            const SizedBox(height: 4),
                            const StatusText(kind: StatusKind.pending, label: 'DRAFT'),
                          ],
                        ),
                      ),
                      TextButton(
                        onPressed: () => GoRouter.of(context).go('/a/solution/${state.lastSolutionId}'),
                        child: Text(
                          'REVIEW →',
                          style: BlockType.monoLabel.copyWith(
                            color: BlockColors.accent,
                            fontSize: 13,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _pick(bool isFrom) async {
    final init = isFrom ? _from : _to;
    final picked = await showDatePicker(
      context: context,
      initialDate: init,
      firstDate: DateTime(init.year, init.month - 1),
      lastDate: DateTime(init.year + 2),
    );
    if (picked == null) return;
    setState(() {
      if (isFrom) {
        _from = picked;
        if (_to.isBefore(_from)) _to = _from.add(const Duration(days: 28));
      } else {
        _to = picked;
      }
    });
  }
}

class _DateField extends StatelessWidget {
  const _DateField({required this.label, required this.value, required this.onTap});
  final String label;
  final DateTime value;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(14),
      child: BlockCard(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(label.toUpperCase(), style: BlockType.monoLabel.copyWith(fontSize: 10)),
            const SizedBox(height: 2),
            Text(DateFormat('d MMM y').format(value), style: BlockType.body),
          ],
        ),
      ),
    );
  }
}

class _ModeSegment extends StatelessWidget {
  const _ModeSegment({required this.value, required this.onChanged});
  final String value;
  final ValueChanged<String> onChanged;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(3),
      decoration: BoxDecoration(
        color: BlockColors.line2,
        borderRadius: BorderRadius.circular(999),
      ),
      child: Row(
        children: [
          Expanded(child: _seg('STRICT', 'strict')),
          Expanded(child: _seg('RELAXED', 'relaxed')),
        ],
      ),
    );
  }

  Widget _seg(String label, String key) {
    final active = value == key;
    return GestureDetector(
      onTap: () => onChanged(key),
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 7),
        decoration: BoxDecoration(
          color: active ? Colors.white : Colors.transparent,
          borderRadius: BorderRadius.circular(999),
        ),
        alignment: Alignment.center,
        child: Text(
          label,
          style: BlockType.monoLabel.copyWith(
            fontSize: 11,
            color: active ? BlockColors.ink1 : BlockColors.ink2,
          ),
        ),
      ),
    );
  }
}

class _OptionRow extends StatelessWidget {
  const _OptionRow({
    required this.title,
    required this.subtitle,
    required this.value,
    required this.onChanged,
  });
  final String title;
  final String subtitle;
  final bool value;
  final ValueChanged<bool> onChanged;

  @override
  Widget build(BuildContext context) {
    return BlockCard(
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: BlockType.body),
                const SizedBox(height: 2),
                Text(subtitle, style: BlockType.bodySm),
              ],
            ),
          ),
          Switch.adaptive(
            value: value,
            onChanged: onChanged,
            activeThumbColor: BlockColors.accent,
          ),
        ],
      ),
    );
  }
}
