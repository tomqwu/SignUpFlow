// Block-Mono ThemeData. Material 3 base + heavy custom overrides per
// brand-spec.md. Two variants — light + dark — selected at runtime via
// `themeProvider` (mobile/lib/theme/theme_provider.dart). Use these as
// MaterialApp.router's `theme` + `darkTheme`.

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

/// Dark variant of the Block-Mono theme. Mirror the light theme's
/// structure but flip the ColorScheme to dark + swap the scaffold
/// background to BlockColors.bgAppDark. Components that read from the
/// active ColorScheme (Material widgets) follow automatically;
/// components that hardcode BlockColors.* values fall back to the same
/// brand palette — see `mobile/lib/theme/colors.dart` for the dark
/// variants used here.
ThemeData buildBlockMonoDarkTheme() {
  final base = ThemeData(
    useMaterial3: true,
    brightness: Brightness.dark,
    colorScheme: const ColorScheme.dark(
      primary: BlockColors.accent,
      onPrimary: Colors.white,
      secondary: BlockColors.ink1Dark,
      onSecondary: Colors.white,
      surface: BlockColors.bgCardDark,
      onSurface: BlockColors.ink1Dark,
      error: BlockColors.danger,
      onError: Colors.white,
    ),
    scaffoldBackgroundColor: BlockColors.bgAppDark,
    fontFamily: GoogleFonts.inter().fontFamily,
  );

  return base.copyWith(
    appBarTheme: const AppBarTheme(
      backgroundColor: BlockColors.bgAppDark,
      surfaceTintColor: Colors.transparent,
      foregroundColor: BlockColors.ink1Dark,
      elevation: 0,
      scrolledUnderElevation: 0,
      centerTitle: false,
    ),
    bottomNavigationBarTheme: BottomNavigationBarThemeData(
      backgroundColor: BlockColors.bgCardDark.withValues(alpha: 0.96),
      selectedItemColor: BlockColors.ink1Dark,
      unselectedItemColor: BlockColors.ink3Dark,
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
      color: BlockColors.line1Dark,
      thickness: 1,
      space: 1,
    ),
    splashFactory: NoSplash.splashFactory,
    highlightColor: Colors.transparent,
  );
}
