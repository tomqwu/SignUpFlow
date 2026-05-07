// LabeledField — Block-Mono themed labeled text input. Extracted from
// the login screen so signup, invitation, and password-reset reuse it.

import 'package:flutter/material.dart';
import 'package:signupflow_mobile/theme/colors.dart';
import 'package:signupflow_mobile/theme/components.dart';
import 'package:signupflow_mobile/theme/typography.dart';

class LabeledField extends StatelessWidget {
  const LabeledField({
    required this.label,
    required this.controller,
    required this.hint,
    super.key,
    this.obscure = false,
    this.keyboard,
    this.autocorrect = false,
    this.textCapitalization = TextCapitalization.none,
  });

  final String label;
  final TextEditingController controller;
  final String hint;
  final bool obscure;
  final TextInputType? keyboard;
  final bool autocorrect;
  final TextCapitalization textCapitalization;

  @override
  Widget build(BuildContext context) {
    return BlockCard(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            label.toUpperCase(),
            style: BlockType.monoLabel.copyWith(fontSize: 10),
          ),
          TextField(
            controller: controller,
            obscureText: obscure,
            keyboardType: keyboard,
            autocorrect: autocorrect,
            enableSuggestions: !obscure && autocorrect,
            textCapitalization: textCapitalization,
            style: BlockType.body,
            decoration: InputDecoration(
              hintText: hint,
              hintStyle: BlockType.body.copyWith(color: BlockColors.ink3),
              border: InputBorder.none,
              isDense: true,
              contentPadding: EdgeInsets.zero,
            ),
          ),
        ],
      ),
    );
  }
}
