// SIGNUP/FLOW wordmark + S app icon mark. See brand-spec.md.

import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import 'package:signupflow_mobile/theme/colors.dart';

class BrandMark extends StatelessWidget {
  const BrandMark({this.size = 64, super.key});

  final double size;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        color: BlockColors.accent,
        borderRadius: BorderRadius.circular(size * 0.224),
      ),
      alignment: Alignment.center,
      child: Text(
        'S',
        style: GoogleFonts.inter(
          fontSize: size * 0.72,
          fontWeight: FontWeight.w700,
          color: Colors.white,
          letterSpacing: -0.06 * size * 0.72,
          height: 1,
        ),
      ),
    );
  }
}

class Wordmark extends StatelessWidget {
  const Wordmark({this.size = 18, super.key});

  final double size;

  @override
  Widget build(BuildContext context) {
    return RichText(
      text: TextSpan(
        style: GoogleFonts.inter(
          fontSize: size,
          fontWeight: FontWeight.w700,
          letterSpacing: -0.025 * size,
          color: BlockColors.ink1,
        ),
        children: [
          const TextSpan(text: 'SIGNUP'),
          TextSpan(
            text: '/',
            style: GoogleFonts.inter(
              fontSize: size,
              fontWeight: FontWeight.w500,
              color: BlockColors.accent,
            ),
          ),
          const TextSpan(text: 'FLOW'),
        ],
      ),
    );
  }
}
