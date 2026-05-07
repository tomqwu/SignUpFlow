// Block-Mono typography. Inter for display/body, JetBrains Mono for data/labels.
// Weights and tracking match mobile/prototype/brand-spec.md.

import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import 'package:signupflow_mobile/theme/colors.dart';

abstract final class BlockType {
  // Display roles — Inter
  static TextStyle displayUpper(double size) => GoogleFonts.inter(
        fontSize: size,
        fontWeight: FontWeight.w700,
        letterSpacing: -0.025 * size,
        color: BlockColors.ink1,
        height: 1.05,
      );

  static TextStyle subhead = GoogleFonts.inter(
    fontSize: 17,
    fontWeight: FontWeight.w600,
    letterSpacing: -0.255,
    color: BlockColors.ink1,
  );

  static TextStyle body = GoogleFonts.inter(
    fontSize: 15,
    fontWeight: FontWeight.w500,
    color: BlockColors.ink1,
    height: 1.4,
  );

  static TextStyle bodySm = GoogleFonts.inter(
    fontSize: 13,
    fontWeight: FontWeight.w400,
    color: BlockColors.ink2,
    height: 1.5,
  );

  static TextStyle caption = GoogleFonts.inter(
    fontSize: 11,
    fontWeight: FontWeight.w500,
    letterSpacing: 0.11,
    color: BlockColors.ink2,
  );

  // Mono roles — JetBrains Mono, always uppercase by convention
  static TextStyle monoLabel = GoogleFonts.jetBrainsMono(
    fontSize: 11,
    fontWeight: FontWeight.w500,
    letterSpacing: 0.88,
    color: BlockColors.ink3,
  );

  static TextStyle monoData = GoogleFonts.jetBrainsMono(
    fontSize: 12,
    fontWeight: FontWeight.w500,
    letterSpacing: 0.48,
    color: BlockColors.ink2,
  );

  static TextStyle monoTiny = GoogleFonts.jetBrainsMono(
    fontSize: 10,
    fontWeight: FontWeight.w500,
    letterSpacing: 0.6,
    color: BlockColors.ink3,
  );
}
