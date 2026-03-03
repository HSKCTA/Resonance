# Resonance Dashboard — Professional UI Guidelines

This file defines layout, visual hierarchy, interaction logic, and data presentation standards for the Resonance Industrial Monitoring Platform.

---

# 1. Core Philosophy

Resonance UI must feel:

• Industrial
• Deterministic
• Data-first
• Low-noise
• Operationally trustworthy

Avoid flashy gradients, excessive glow effects, or overly animated components.

This is an engineering tool — not a marketing website.

---

# 2. Layout System

## Grid System

• Use 12-column grid layout
• 24px outer padding
• 16px internal card padding
• 8px spacing scale (8 / 16 / 24 / 32)

Never use arbitrary spacing.

---

# 3. Visual Hierarchy

## Typography Scale

• Base font size: 14px
• Section titles: 16px semi-bold
• Metric values: 28–36px bold
• Labels: 12px medium
• Secondary metadata: 11px muted

Font: Inter / IBM Plex Sans / SF Pro (neutral, professional)

No decorative fonts.

---

# 4. Color System

Limit color usage.

### Background

• Primary background: #0F172A
• Card background: #111827
• Border: #1F2937

### Semantic Colors

• Healthy: #22C55E
• Warning: #F59E0B
• Critical: #EF4444
• Neutral metric: #3B82F6

Rules:
• Never use more than 3 active accent colors on one screen.
• Avoid bright neon gradients.
• Alerts must be red only when critical.

---

# 5. Card Design

Cards must:

• Have 8px border radius
• Subtle 1px border
• No heavy shadows
• Clear top-left title alignment
• Top-right optional action icon

Do NOT center titles.

---

# 6. Graph Standards

All charts must:

• Use dark theme with subtle grid lines
• Remove heavy glow or bright axes
• Use thin 2px lines
• Use filled area at 10–15% opacity only
• Y-axis labels muted
• X-axis minimal

Avoid:
• Over-animated transitions
• Excessively thick lines
• High-saturation colors

---

# 7. Alert Design

Alerts must be:

• Text-driven, not icon-heavy
• Positioned in a dedicated alert strip
• Never overlay graph content

Alert priority:

1. Critical
2. Warning
3. Info

Only show the highest priority active alert per node.

---

# 8. Data Density Rules

Industrial dashboards must prioritize:

• Information clarity over aesthetics
• Simultaneous multi-node visibility
• Compact layout

Avoid large empty spaces.
Avoid oversized gauges.

Replace circular gauges with:

• Linear health bars
• Percentage meters
• Numeric + small sparkline

---

# 9. Node Panel Design

Left panel must:

• Show node name
• Machine type
• Small status dot
• Last update time

No large glowing indicators.

---

# 10. Latency Panel

Pipeline latency must:

• Be shown as segmented horizontal bar
• DSP | AI | ALERT
• Each labeled with ms
• Total latency right-aligned

No 3D effects.

---

# 11. Spectrogram Design

• Use perceptually uniform colormap (viridis / plasma)
• Avoid rainbow colormap
• Add frequency axis label
• Add amplitude legend

---

# 12. Professional Polish Checklist

Before finalizing design:

✓ Consistent padding
✓ Consistent typography scale
✓ No random color usage
✓ No unnecessary icons
✓ Balanced layout symmetry
✓ Alert semantics clear
✓ Works at 1920x1080 resolution
✓ Works on laptop screen

---

# 13. What To Avoid

✗ Neon gradients
✗ Heavy drop shadows
✗ Overuse of glassmorphism
✗ Big circular gauges
✗ Inconsistent alignment
✗ Unnecessary animation
✗ Large empty hero sections

---

# 14. Benchmark Reference

Design should feel closer to:

• Grafana
• Datadog
• Azure Monitor
• Siemens MindSphere
• Industrial SCADA dashboards

Not:

• Crypto dashboards
• Gaming UI
• Marketing landing pages