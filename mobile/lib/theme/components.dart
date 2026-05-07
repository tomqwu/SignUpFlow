// Block-Mono custom widgets — the building blocks the prototype HTML used,
// expressed as Flutter widgets. See mobile/prototype/brand-spec.md.

import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import 'package:signupflow_mobile/theme/colors.dart';
import 'package:signupflow_mobile/theme/typography.dart';

/// Solid CTA. `kind` selects the visual variant.
enum BlockButtonKind { primary, go, secondary, destructive }

class BlockButton extends StatelessWidget {
  const BlockButton({
    required this.label,
    required this.onPressed,
    this.kind = BlockButtonKind.primary,
    super.key,
  });

  final String label;
  final VoidCallback? onPressed;
  final BlockButtonKind kind;

  @override
  Widget build(BuildContext context) {
    final (bg, fg, border) = switch (kind) {
      BlockButtonKind.primary => (BlockColors.ink1, Colors.white, null),
      BlockButtonKind.go => (BlockColors.accent, Colors.white, null),
      BlockButtonKind.secondary => (Colors.white, BlockColors.ink1, BlockColors.line1),
      BlockButtonKind.destructive => (Colors.white, BlockColors.danger, BlockColors.line1),
    };
    return SizedBox(
      width: double.infinity,
      child: Material(
        color: bg,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(999),
          side: border != null ? BorderSide(color: border) : BorderSide.none,
        ),
        child: InkWell(
          onTap: onPressed,
          borderRadius: BorderRadius.circular(999),
          child: Padding(
            padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 20),
            child: Center(
              child: Text(
                label.toUpperCase(),
                style: GoogleFonts.inter(
                  color: fg,
                  fontSize: 13,
                  fontWeight: FontWeight.w700,
                  letterSpacing: 0.52,
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

/// `[ 10:00–11:30 ]` calendar-app signature chip.
class TimeChip extends StatelessWidget {
  const TimeChip(this.text, {super.key});
  final String text;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: BlockColors.accentSoft,
        borderRadius: BorderRadius.circular(6),
      ),
      child: Text(
        text,
        style: GoogleFonts.jetBrainsMono(
          fontSize: 11,
          fontWeight: FontWeight.w500,
          letterSpacing: 0.22,
          color: BlockColors.accentInk,
        ),
      ),
    );
  }
}

/// Bordered uppercase mono pill — used for roles like USHER, GREETER.
class RoleChip extends StatelessWidget {
  const RoleChip(this.text, {super.key});
  final String text;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        color: Colors.white,
        border: Border.all(color: BlockColors.line1),
        borderRadius: BorderRadius.circular(6),
      ),
      child: Text(
        text.toUpperCase(),
        style: GoogleFonts.jetBrainsMono(
          fontSize: 10,
          fontWeight: FontWeight.w500,
          letterSpacing: 0.6,
          color: BlockColors.ink2,
        ),
      ),
    );
  }
}

/// Status text with leading colored dot. Always text + dot, never just a dot.
enum StatusKind { confirmed, pending, declined, neutral }

class StatusText extends StatelessWidget {
  const StatusText({
    required this.kind,
    required this.label,
    super.key,
  });

  final StatusKind kind;
  final String label;

  Color get _color => switch (kind) {
        StatusKind.confirmed => BlockColors.success,
        StatusKind.pending => BlockColors.warning,
        StatusKind.declined => BlockColors.danger,
        StatusKind.neutral => BlockColors.ink3,
      };

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        Text('●', style: TextStyle(color: _color, fontSize: 8)),
        const SizedBox(width: 4),
        Text(
          label.toUpperCase(),
          style: GoogleFonts.jetBrainsMono(
            fontSize: 10,
            fontWeight: FontWeight.w500,
            letterSpacing: 0.8,
            color: _color,
          ),
        ),
      ],
    );
  }
}

/// Section label — small UPPERCASE mono caption above a group of cards.
class MonoLabel extends StatelessWidget {
  const MonoLabel(this.text, {this.trailing, super.key});
  final String text;
  final Widget? trailing;

  @override
  Widget build(BuildContext context) {
    final label = Text(text.toUpperCase(), style: BlockType.monoLabel);
    const pad = EdgeInsets.fromLTRB(4, 22, 4, 8);
    if (trailing == null) {
      return Padding(padding: pad, child: label);
    }
    return Padding(
      padding: pad,
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [label, trailing!],
      ),
    );
  }
}

/// White surface card with hairline border — Block-Mono uses no shadows.
class BlockCard extends StatelessWidget {
  const BlockCard({
    required this.child,
    this.padding = const EdgeInsets.all(14),
    this.color,
    this.borderColor,
    super.key,
  });

  final Widget child;
  final EdgeInsets padding;
  final Color? color;
  final Color? borderColor;

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: color ?? BlockColors.bgCard,
        border: Border.all(color: borderColor ?? BlockColors.line1),
        borderRadius: BorderRadius.circular(14),
      ),
      padding: padding,
      child: child,
    );
  }
}

/// Avatar — initials in a teal-tone disc. No profile photos in MVP.
class AvatarBadge extends StatelessWidget {
  const AvatarBadge({required this.name, this.size = 36, super.key});

  final String name;
  final double size;

  static const _palette = [
    Color(0xFF0F766E),
    Color(0xFF0D5F58),
    Color(0xFF14807A),
    Color(0xFF1F8E87),
    Color(0xFFB45309),
  ];

  @override
  Widget build(BuildContext context) {
    final initials = name
        .split(' ')
        .where((s) => s.isNotEmpty)
        .take(2)
        .map((s) => s[0].toUpperCase())
        .join();
    final bg = _palette[name.codeUnitAt(0) % _palette.length];
    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(color: bg, shape: BoxShape.circle),
      alignment: Alignment.center,
      child: Text(
        initials,
        style: GoogleFonts.inter(
          color: Colors.white,
          fontWeight: FontWeight.w700,
          fontSize: size * 0.36,
          letterSpacing: -0.4,
        ),
      ),
    );
  }
}

/// Big number + label cell used in dashboards.
class KpiCell extends StatelessWidget {
  const KpiCell({
    required this.value,
    required this.label,
    this.unit,
    this.accent = false,
    super.key,
  });

  final String value;
  final String label;
  final String? unit;
  final bool accent;

  @override
  Widget build(BuildContext context) {
    final color = accent ? BlockColors.accent : BlockColors.ink1;
    return BlockCard(
      padding: const EdgeInsets.fromLTRB(14, 16, 14, 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          RichText(
            text: TextSpan(
              style: GoogleFonts.inter(
                fontSize: 26,
                fontWeight: FontWeight.w700,
                letterSpacing: -0.65,
                color: color,
                height: 1.05,
              ),
              children: [
                TextSpan(text: value),
                if (unit != null)
                  TextSpan(
                    text: unit,
                    style: GoogleFonts.inter(
                      fontSize: 13,
                      fontWeight: FontWeight.w500,
                      color: BlockColors.ink2,
                      letterSpacing: 0,
                    ),
                  ),
              ],
            ),
          ),
          const SizedBox(height: 4),
          Text(label.toUpperCase(), style: BlockType.monoTiny),
        ],
      ),
    );
  }
}

/// Page-title row — UPPERCASE Inter 700 with brand-spec tracking.
class PageTitle extends StatelessWidget {
  const PageTitle(this.text, {this.trailingCount, super.key});
  final String text;
  final String? trailingCount;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(20, 4, 20, 16),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.baseline,
        textBaseline: TextBaseline.alphabetic,
        children: [
          Text(text.toUpperCase(), style: BlockType.displayUpper(28)),
          if (trailingCount != null) ...[
            const SizedBox(width: 8),
            Text(
              trailingCount!,
              style: BlockType.displayUpper(28).copyWith(color: BlockColors.ink3),
            ),
          ],
        ],
      ),
    );
  }
}
