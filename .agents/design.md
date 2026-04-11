# Design System — Donezo × Prodmast

> A unified design language combining the structured productivity aesthetic of **Donezo** (task/project dashboard) and the polished marketing identity of **Prodmast** (manufacturing SaaS landing page).

---

## 1. Brand & Vision

| Attribute     | Description |
|---------------|-------------|
| **Tone**      | Professional, confident, modern — authoritative without being cold |
| **Aesthetic** | Clean enterprise SaaS — generous whitespace, bold type, dark accent panels |
| **Audience**  | B2B users: project managers, ops teams, manufacturing businesses |
| **Feeling**   | Efficient. Trustworthy. Forward-moving. |

---

## 2. Color Palette

### Primary
| Token                  | Hex       | Usage |
|------------------------|-----------|-------|
| `--color-primary`      | `#1A4D2E` | Primary actions, active nav, CTA buttons |
| `--color-primary-dark` | `#0F2D1A` | Hover states, dark sections, footer |
| `--color-primary-light`| `#E8F5EC` | Subtle backgrounds, tag fills, highlights |

### Neutral
| Token                   | Hex       | Usage |
|-------------------------|-----------|-------|
| `--color-bg`            | `#FFFFFF` | Page background |
| `--color-bg-secondary`  | `#F8F9FA` | Card backgrounds, sidebar |
| `--color-border`        | `#E5E7EB` | Dividers, card borders |
| `--color-text-primary`  | `#111827` | Headings, body copy |
| `--color-text-secondary`| `#6B7280` | Subtitles, labels, meta |
| `--color-text-muted`    | `#9CA3AF` | Placeholder text, disabled |

### Status
| Token               | Hex       | Usage |
|---------------------|-----------|-------|
| `--color-success`   | `#22C55E` | Completed status, positive deltas |
| `--color-warning`   | `#F59E0B` | In Progress, pending indicators |
| `--color-danger`    | `#EF4444` | Error states, overdue |
| `--color-info`      | `#3B82F6` | Info badges, secondary actions |

### Dark Sections
| Token                    | Hex       | Usage |
|--------------------------|-----------|-------|
| `--color-dark-bg`        | `#0F1F14` | Dark CTA panels, feature sections |
| `--color-dark-surface`   | `#1A3322` | Cards within dark sections |
| `--color-dark-text`      | `#F1F5F0` | Text on dark backgrounds |

---

## 3. Typography

### Font Families
```css
--font-display: 'Syne', sans-serif;      /* Headings, hero titles */
--font-body:    'DM Sans', sans-serif;   /* UI text, body copy */
--font-mono:    'JetBrains Mono', monospace; /* Time tracker, data values */
```

> **Rationale:** Syne provides an editorial, slightly geometric authority for display use. DM Sans is legible and friendly for dense UI. JetBrains Mono gives numerical data a precise, techy clarity.

### Scale
| Token              | Size     | Weight | Line Height | Usage |
|--------------------|----------|--------|-------------|-------|
| `--text-hero`      | 48–56px  | 700    | 1.1         | Landing page H1 |
| `--text-h1`        | 36px     | 700    | 1.2         | Page titles |
| `--text-h2`        | 28px     | 600    | 1.3         | Section headings |
| `--text-h3`        | 20px     | 600    | 1.4         | Card titles, subsections |
| `--text-body-lg`   | 16px     | 400    | 1.6         | Primary body text |
| `--text-body`      | 14px     | 400    | 1.6         | UI labels, descriptions |
| `--text-sm`        | 12px     | 400    | 1.5         | Meta, captions, badges |
| `--text-stat`      | 40–48px  | 700    | 1.0         | Dashboard stat numbers |

---

## 4. Spacing

Based on a **4px base unit**.

| Token          | Value  | Usage |
|----------------|--------|-------|
| `--space-1`    | 4px    | Micro gaps |
| `--space-2`    | 8px    | Icon padding, tight spacing |
| `--space-3`    | 12px   | Inner card padding |
| `--space-4`    | 16px   | Standard element gap |
| `--space-5`    | 20px   | Section sub-gaps |
| `--space-6`    | 24px   | Card padding |
| `--space-8`    | 32px   | Large component gap |
| `--space-10`   | 40px   | Section padding |
| `--space-16`   | 64px   | Page section margins |
| `--space-24`   | 96px   | Hero/landing section padding |

---

## 5. Border Radius

| Token             | Value  | Usage |
|-------------------|--------|-------|
| `--radius-sm`     | 6px    | Badges, tags, small buttons |
| `--radius-md`     | 10px   | Buttons, input fields |
| `--radius-lg`     | 16px   | Cards, panels |
| `--radius-xl`     | 24px   | Large feature cards, modals |
| `--radius-full`   | 9999px | Pills, avatars, toggles |

---

## 6. Shadows & Elevation

```css
--shadow-sm:  0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
--shadow-md:  0 4px 12px rgba(0,0,0,0.08), 0 2px 6px rgba(0,0,0,0.05);
--shadow-lg:  0 10px 30px rgba(0,0,0,0.10), 0 4px 12px rgba(0,0,0,0.06);
--shadow-xl:  0 20px 50px rgba(0,0,0,0.12);
--shadow-primary: 0 8px 24px rgba(26, 77, 46, 0.28); /* Green glow for primary buttons */
```

---

## 7. Components

### Buttons

| Variant     | Background           | Text      | Hover                      |
|-------------|----------------------|-----------|----------------------------|
| Primary     | `--color-primary`    | White     | `--color-primary-dark` + lift shadow |
| Secondary   | White                | `--color-text-primary` | Border darkens, bg: `--color-bg-secondary` |
| Ghost       | Transparent          | `--color-primary` | `--color-primary-light` bg |
| Destructive | `--color-danger`     | White     | Darken 10% |

- Padding: `10px 20px` (default), `12px 28px` (large)
- Border radius: `--radius-md`
- Font: `--font-body`, 14px, weight 500
- Transition: `all 0.2s ease`

---

### Cards

```
Background: --color-bg
Border: 1px solid --color-border
Border Radius: --radius-lg
Padding: --space-6
Box Shadow: --shadow-sm
Hover: --shadow-md + translateY(-2px)
Transition: 0.2s ease
```

**Dark Card Variant** (used in stats, CTA sections):
```
Background: --color-primary
Color: white
Border: none
```

---

### Badges / Status Tags

| Status      | Background             | Text Color         |
|-------------|------------------------|--------------------|
| Completed   | `#DCFCE7`              | `#15803D`          |
| In Progress | `#FEF9C3`              | `#A16207`          |
| Pending     | `#FEE2E2`              | `#B91C1C`          |
| On Discuss  | `#EDE9FE`              | `#6D28D9`          |

- Font size: `--text-sm`
- Font weight: 500
- Padding: `3px 10px`
- Border radius: `--radius-full`

---

### Navigation Sidebar (Dashboard)

- Width: `240px`
- Background: `#FFFFFF` with right border `--color-border`
- Active item: `--color-primary-light` background, `--color-primary` text & left border accent (3px)
- Logo section height: `64px`
- Nav label sections (`MENU`, `GENERAL`): `--text-sm`, uppercase, letter-spacing `0.08em`, `--color-text-muted`

---

### Top Navigation Bar (Landing)

- Height: `64px`
- Background: White with `--shadow-sm` on scroll
- Logo: `--color-primary` green icon + brand name in `--font-display`
- Nav links: `--text-body`, weight 500, hover: `--color-primary`
- CTA button: Primary variant

---

### Stat / KPI Cards

```
Large Number: --text-stat, --font-mono or --font-display, --color-text-primary
Label: --text-sm, --color-text-secondary, uppercase
Delta Badge: Small pill — green for positive (+↑), neutral for flat
Arrow icon: Top-right corner, --color-text-muted
```

---

### Pricing Cards

- Standard: White background, border `--color-border`
- Featured/Enterprise: Dark background `--color-primary-dark`, white text
- Price: `--text-h1`, `--font-display`
- Feature list: checkmarks in `--color-success`, `--text-body`

---

## 8. Data Visualization

### Bar Charts (Weekly Analytics)
- Active bar: `--color-primary` (solid)
- Inactive bars: Diagonal hatch pattern (`rgba(0,0,0,0.08)`) on `--color-bg-secondary`
- Chart height: ~120px inside cards
- No axis lines — clean, minimal

### Gauge / Donut (Project Progress)
- Track color: `--color-border`
- Fill: `--color-primary`
- Center value: `--text-h2`, `--font-mono`

### Time Tracker Display
```
Background: --color-primary-dark
Font: --font-mono, 36–40px, white
Display: HH:MM:SS format
```

---

## 9. Iconography

- **Style**: Outline icons, 1.5px stroke weight, rounded caps
- **Library**: Lucide or Heroicons (outline variant)
- **Size grid**: 16px (inline), 20px (nav), 24px (feature icons), 40px (section icons)
- **Color**: Inherits text color or `--color-primary` for active/accented states

---

## 10. Layout Grid

### Dashboard App
```
Sidebar: 240px fixed
Main content: fluid, min 0
Top bar: 64px fixed
Content padding: 32px
Card grid: CSS Grid, auto-fill, minmax(240px, 1fr), gap: 20px
```

### Landing Page
```
Max width: 1200px
Horizontal padding: clamp(20px, 5vw, 80px)
Section padding vertical: 80–120px
Column grid: 12-column, gap: 24px
Hero: centered, max-width 800px for copy
Feature grid: 3 columns (desktop), 2 (tablet), 1 (mobile)
```

---

## 11. Motion & Animation

```css
--transition-fast:   0.15s ease;
--transition-base:   0.25s ease;
--transition-slow:   0.4s cubic-bezier(0.4, 0, 0.2, 1);
--transition-spring: 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
```

### Usage Guidelines
- **Page load**: Stagger card reveals with `animation-delay` increments of `60ms`
- **Hover states**: `--transition-fast` for color, `--transition-base` for transform
- **Modal / Drawer open**: `--transition-slow` with slight scale-up from 0.97
- **Stat counters**: Count-up animation on first viewport entry
- **Progress bars**: Animate width from 0 on mount, `--transition-slow`
- **Avoid**: Perpetual looping animations on content (use only for loading spinners)

---

## 12. Responsive Breakpoints

| Name     | Min-width | Notes |
|----------|-----------|-------|
| `sm`     | 640px     | Mobile landscape |
| `md`     | 768px     | Tablet |
| `lg`     | 1024px    | Small desktop, sidebar collapses |
| `xl`     | 1280px    | Full layout |
| `2xl`    | 1536px    | Wide screens |

**Mobile behavior:**
- Sidebar converts to bottom nav or hamburger drawer
- Stat cards stack vertically
- Landing hero copy scales down via `clamp()`
- Pricing cards stack to single column

---

## 13. Accessibility

- Minimum contrast ratio: **4.5:1** for body text, **3:1** for large text and UI components
- All interactive elements: visible `:focus-visible` ring — `2px solid --color-primary`, offset 2px
- Touch targets: minimum `44×44px`
- Animated elements: respect `prefers-reduced-motion` — disable transforms/transitions
- Form inputs: always paired with visible `<label>`, never placeholder-only
- Status colors: never rely on color alone — pair with icon or text label

---

## 14. File & Asset Conventions

```
/assets
  /icons        → SVG sprites or individual .svg files (outline style)
  /images       → Optimized .webp, with .jpg fallbacks
  /fonts        → Self-hosted woff2 for Syne + DM Sans + JetBrains Mono

/styles
  /tokens.css   → All CSS custom properties defined on :root
  /base.css     → Reset, body defaults, typography scale
  /components/  → One file per component
  /layouts/     → Sidebar, grid, page shell
  /utilities/   → Spacing helpers, text helpers
```

---

*Last updated: April 2026*