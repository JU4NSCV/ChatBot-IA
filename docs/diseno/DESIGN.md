---
name: Academic AI Ethics Interface
colors:
  surface: '#111415'
  surface-dim: '#111415'
  surface-bright: '#37393b'
  surface-container-lowest: '#0c0f10'
  surface-container-low: '#191c1e'
  surface-container: '#1d2022'
  surface-container-high: '#282a2c'
  surface-container-highest: '#323537'
  on-surface: '#e1e2e4'
  on-surface-variant: '#e0c0b1'
  inverse-surface: '#e1e2e4'
  inverse-on-surface: '#2e3132'
  outline: '#a78b7d'
  outline-variant: '#584236'
  surface-tint: '#ffb68e'
  primary: '#ffb68e'
  on-primary: '#542200'
  primary-container: '#ff7a1a'
  on-primary-container: '#5e2700'
  inverse-primary: '#9c4500'
  secondary: '#bbc3ff'
  on-secondary: '#001d93'
  secondary-container: '#0231de'
  on-secondary-container: '#b1bbff'
  tertiary: '#c0c5e0'
  on-tertiary: '#2a3045'
  tertiary-container: '#9a9fb9'
  on-tertiary-container: '#30364c'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#ffdbca'
  primary-fixed-dim: '#ffb68e'
  on-primary-fixed: '#331200'
  on-primary-fixed-variant: '#773300'
  secondary-fixed: '#dee0ff'
  secondary-fixed-dim: '#bbc3ff'
  on-secondary-fixed: '#000f5d'
  on-secondary-fixed-variant: '#002ccd'
  tertiary-fixed: '#dce1fd'
  tertiary-fixed-dim: '#c0c5e0'
  on-tertiary-fixed: '#151b2f'
  on-tertiary-fixed-variant: '#40465c'
  background: '#111415'
  on-background: '#e1e2e4'
  surface-variant: '#323537'
typography:
  display:
    fontFamily: Plus Jakarta Sans
    fontSize: 3.5rem
    fontWeight: '800'
    lineHeight: 4rem
    letterSpacing: -0.03em
  display-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 2.25rem
    fontWeight: '800'
    lineHeight: 2.75rem
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 2.5rem
    fontWeight: '700'
    lineHeight: 3rem
    letterSpacing: -0.02em
  headline-lg-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 1.75rem
    fontWeight: '700'
    lineHeight: 2.25rem
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 1.75rem
    fontWeight: '700'
    lineHeight: 2.25rem
    letterSpacing: -0.015em
  headline-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 1.25rem
    fontWeight: '600'
    lineHeight: 1.75rem
    letterSpacing: -0.01em
  body-lg:
    fontFamily: Inter
    fontSize: 1.125rem
    fontWeight: '400'
    lineHeight: 1.75rem
  body-md:
    fontFamily: Inter
    fontSize: 1rem
    fontWeight: '400'
    lineHeight: 1.5rem
  body-sm:
    fontFamily: Inter
    fontSize: 0.875rem
    fontWeight: '400'
    lineHeight: 1.25rem
  label-lg:
    fontFamily: JetBrains Mono
    fontSize: 0.875rem
    fontWeight: '600'
    lineHeight: 1.25rem
    letterSpacing: 0.06em
  label-md:
    fontFamily: JetBrains Mono
    fontSize: 0.75rem
    fontWeight: '500'
    lineHeight: 1rem
    letterSpacing: 0.08em
  label-sm:
    fontFamily: JetBrains Mono
    fontSize: 0.6875rem
    fontWeight: '500'
    lineHeight: 0.875rem
    letterSpacing: 0.1em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  gutter: 1.5rem
  gutter-sm: 1rem
  gutter-lg: 2rem
  margin: 1.5rem
  margin-sm: 1rem
  margin-lg: 3rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2.5rem
---

## Brand & Style

The design system establishes a high-trust, rigorous, and technologically progressive environment tailored for DilemaBot—an AI ethics evaluation platform engineered at Universidad Técnica Particular de Loja (UTPL). The interface balances scholarly precision with the responsiveness of modern conversational AI. It reflects journalistic accountability, philosophical inquiry, and pedagogical clarity.

The aesthetic philosophy is **Academic Structuralism with Tactile Glass Surfaces**. It avoids toy-like conversational tropes in favor of an investigative, editorial atmosphere: deliberate information hierarchy, disciplined data density, architectural framing, and prominent verification tags. Transparent layers signify institutional openness, while deep nocturnal foundations convey analytical weight and focus.

## Colors

The palette establishes an authoritative dark canvas punctuated by high-signal accents that guide ethical discernment and systemic feedback.

- **Primary Dark Base (`#141A2E`)**: Deep Night Blue acts as the structural canvas, reducing eye fatigue during long deliberative sessions while lending institutional gravity.
- **Primary Accent (`#FF7A1A`)**: Vibrant Orange functions strictly as the primary interactive catalyst—applied to key conversational triggers, active ethical tension states, validation steps, and decision confirmations.
- **Secondary Accent (`#3D5AFE`)**: Electric Blue represents verified AI provenance, algorithmic signals, cross-referencing nodes, and technological processes.
- **Neutral Light (`#F3F4F6`) & Crisp White (`#FFFFFF`)**: Deployed for high-contrast typographic rendering on dark containers, elevated white cards in analytical split views, and distinct quote modules.

Color is functional, not ornamental: neutral grays structure conversational history, vibrant orange flags decisive moral trade-offs, and electric blue demarcates references and model citations.

## Typography

The typographic hierarchy establishes clear boundaries between narrative content, academic prose, and technical metadata:

1. **Headlines (`Plus Jakarta Sans`)**: Delivers geometric structure, assertive modernism, and editorial authority. Tight negative letter-spacing ensures optical balance across prominent dilemma prompts and thesis statements.
2. **Body Prose (`Inter`)**: Chosen for neutral legibility during extensive textual reviews, contextual scenario readouts, and philosophical debate threads.
3. **Badges & Provenance (`JetBrains Mono`)**: Strict uppercase styling with deliberate positive tracking (`0.06em` to `0.1em`). Used exclusively for index counters (e.g., `01 · QUÉ HACE`), verified corpus citations (e.g., `↳ Fuente: corpus validado`), schema properties, and machine states.

## Layout & Spacing

The layout model uses a 12-column responsive fluid grid designed around dual analytical columns: the deliberative thread (chat context) alongside an evidence/dilemma inspector panel.

- **Desktop (1024px and above)**: 12 columns with `2rem` gutters and `3rem` canvas margins. Asymmetrical distribution provides 7 columns for conversational reasoning and 5 columns for source citations, metrics, and ethical rubrics.
- **Tablet (768px – 1023px)**: 8 columns with `1.5rem` gutters and `1.5rem` outer margins. Secondary analytical panels collapse into slide-over verification drawers.
- **Mobile (< 768px)**: 4 columns with `1rem` gutters and `1rem` margins. The interface transitions to a stacked conversational feed with anchored persistent verification pills and bottom-sheet drawers for citations.

Internal element rhythm is governed strictly by the `space-*` scale to maintain systematic visual alignment between metadata tags, chat bubbles, and prompt cards.

## Elevation & Depth

Visual hierarchy uses frosted glassmorphism over low-luminance deep surfaces, paired with precise hairline borders rather than heavy drop shadows:

- **Surface Base (Ground)**: Deep night blue (`#141A2E`) creating zero-elevation depth.
- **Tier 1 (Surface Canvas / Inspector Panels)**: Dark tint (`rgba(255, 255, 255, 0.03)`) with a 1px continuous border of `rgba(255, 255, 255, 0.08)`.
- **Tier 2 (Embedded Chat Cards & Dilemma Modules)**: Translucent surface (`rgba(20, 26, 46, 0.65)`) over dynamic content with `backdrop-filter: blur(16px)` and border accents (`rgba(61, 90, 254, 0.2)` on secondary focus or `rgba(255, 122, 26, 0.3)` on ethical inflection nodes).
- **Tier 3 (Floating Action Inputs & Modals)**: Subtle directional illumination via an ambient glow (`box-shadow: 0 12px 32px -4px rgba(0, 0, 0, 0.45), 0 0 0 1px rgba(255, 255, 255, 0.12)`).
- **Light Context Split**: Light secondary surfaces use pure white (`#FFFFFF`) with `1px solid #E5E7EB` borders and sharp, diffused ambient shadow (`0 4px 20px rgba(20, 26, 46, 0.06)`).

## Shapes

The interface employs a balanced corner radius of `0.5rem` (8px) as its base, extending to `1rem` (16px) for embedded message envelopes and secondary cards, and `1.5rem` (24px) for master dialogue viewports and modal panels. 

This calibrated softness prevents visual harshness in dense ethical evaluations while maintaining the discipline expected of an institutional academic tool. Citations, chips, and micro-labels maintain crisp, semi-rigid geometry with `0.25rem` corners or strict pill geometry when used as state badges.

## Components

### Buttons
- **Primary Action (Deliberate / Submit)**: Solid fill in Vibrant Orange (`#FF7A1A`), text in deep night blue, font-weight 600. Soft glow hover state (`box-shadow: 0 0 16px rgba(255, 122, 26, 0.35)`).
- **Secondary Action (Inspect / Trace Corpus)**: Electric blue outline (`1.5px solid #3D5AFE`) with transparent background, hover fills to `rgba(61, 90, 254, 0.12)`.
- **Ghost Utility**: Monospace or compact sans label, zero background, `rgba(243, 244, 246, 0.7)` typography, shifts to full contrast white on hover.

### Chips & Provenance Tags
- Structural tags display in uppercase JetBrains Mono.
- **Corpus Verification Tag**: Dark translucent background (`rgba(61, 90, 254, 0.1)`), hairline border (`rgba(61, 90, 254, 0.3)`), electric blue text with a leading monospace glyph (`↳ Fuente: corpus validado`).
- **Phase Indicators**: Fixed numerical indices (`01 · QUÉ HACE`, `02 · CRITERIO ÉTICO`) styled with low-opacity borders and subtle letter spacing.

### Input Fields & Prompt Consoles
- Large conversational console framed with subtle glassmorphism (`backdrop-filter: blur(12px)`), `rgba(255, 255, 255, 0.05)` fill, and `1px solid rgba(255, 255, 255, 0.12)`.
- Active focus state dynamically transitions border to Electric Blue (`#3D5AFE`) or Vibrant Orange (`#FF7A1A`) depending on contextual evaluation state.

### Embedded Chat Cards
- **Bot Response (DilemaBot)**: Frosted card with deep night blue backdrop, framed by a soft hairline left border in Electric Blue. Text rendered in high-legibility Inter.
- **User Prompt**: Clean, compact container with minimal opacity (`rgba(255, 255, 255, 0.06)`), positioned flush right with rounded corners (16px).
- **Ethical Dilemma Divergence Node**: Highlighting divergent paths with a dual card setup; left accent line in vibrant orange indicating moral counterweights and consequence matrices.

### Lists & Citations
- Editorial tabular lists with clean divider lines (`1px solid rgba(255, 255, 255, 0.06)`).
- Nested blockquotes for journalistic excerpts: left-bordered with a 2px vertical stroke in `#3D5AFE`, using high-contrast text (`#F3F4F6`) over subtle shaded backgrounds.

### Checkboxes & Radio Selectors
- Custom square-rounded boxes with `0.25rem` corners; selected states populated with solid `#FF7A1A` and crisp dark check icons for rapid assessment reviews.