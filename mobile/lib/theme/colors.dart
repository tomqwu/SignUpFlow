// Block-Mono palette — see mobile/prototype/brand-spec.md for canonical values.
// Don't add colors that aren't in the spec without updating the spec first.

import 'package:flutter/material.dart';

abstract final class BlockColors {
  static const bgPage = Color(0xFFF0EFEC);
  static const bgApp = Color(0xFFFAFAF9);
  static const bgCard = Color(0xFFFFFFFF);

  static const ink1 = Color(0xFF18181B);
  static const ink2 = Color(0xFF52525B);
  static const ink3 = Color(0xFFA1A1AA);

  static const line1 = Color(0xFFE4E4E7);
  static const line2 = Color(0xFFF4F4F5);

  static const accent = Color(0xFF0F766E);
  static const accentSoft = Color(0xFFCCFBF1);
  static const accentInk = Color(0xFF134E4A);

  static const success = Color(0xFF15803D);
  static const warning = Color(0xFFB45309);
  static const danger = Color(0xFFB91C1C);

  // Dark variants for `buildBlockMonoDarkTheme()`. Picked to mirror the
  // brightness inversion of the light palette while keeping the accent
  // and status colors unchanged (Block-Mono brand: accent stays warm
  // teal in both modes). Surfaces invert; foregrounds invert.
  static const bgAppDark = Color(0xFF09090B);
  static const bgCardDark = Color(0xFF18181B);

  static const ink1Dark = Color(0xFFFAFAF9);
  static const ink2Dark = Color(0xFFD4D4D8);
  static const ink3Dark = Color(0xFF71717A);

  static const line1Dark = Color(0xFF27272A);
}
