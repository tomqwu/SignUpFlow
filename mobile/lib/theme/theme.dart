// Block-Mono ThemeData. Material 3 base + heavy custom overrides per
// brand-spec.md. Use this as the single MaterialApp.theme.

import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import 'package:signupflow_mobile/theme/colors.dart';

ThemeData buildBlockMonoTheme() {
  final base = ThemeData(
    useMaterial3: true,
    colorScheme: const ColorScheme.light(
      primary: BlockColors.accent,
      onPrimary: Colors.white,
      secondary: BlockColors.ink1,
      onSecondary: Colors.white,
      surface: BlockColors.bgCard,
      onSurface: BlockColors.ink1,
      error: BlockColors.danger,
      onError: Colors.white,
    ),
    scaffoldBackgroundColor: BlockColors.bgApp,
    fontFamily: GoogleFonts.inter().fontFamily,
  );

  return base.copyWith(
    appBarTheme: const AppBarTheme(
      backgroundColor: BlockColors.bgApp,
      surfaceTintColor: Colors.transparent,
      foregroundColor: BlockColors.ink1,
      elevation: 0,
      scrolledUnderElevation: 0,
      centerTitle: false,
    ),
    bottomNavigationBarTheme: BottomNavigationBarThemeData(
      backgroundColor: Colors.white.withValues(alpha: 0.96),
      selectedItemColor: BlockColors.ink1,
      unselectedItemColor: BlockColors.ink3,
      type: BottomNavigationBarType.fixed,
      selectedLabelStyle: GoogleFonts.jetBrainsMono(
        fontSize: 9,
        fontWeight: FontWeight.w500,
        letterSpacing: 0.72,
      ),
      unselectedLabelStyle: GoogleFonts.jetBrainsMono(
        fontSize: 9,
        fontWeight: FontWeight.w500,
        letterSpacing: 0.72,
      ),
      showUnselectedLabels: true,
    ),
    dividerTheme: const DividerThemeData(
      color: BlockColors.line1,
      thickness: 1,
      space: 1,
    ),
    splashFactory: NoSplash.splashFactory,
    highlightColor: Colors.transparent,
  );
}
