# CivicLens Dispatch - Design System (Day 28)

## Overview

A clean, professional design system for emergency dispatch software.

## Design Principles

1. **Clarity** - Information must be easy to scan and understand
2. **Efficiency** - Minimize clicks and cognitive load
3. **Reliability** - Consistent, predictable interface
4. **Accessibility** - Keyboard navigation, clear contrast
5. **Responsiveness** - Works on all screen sizes

## Color Palette

### Primary Colors

| Color | Hex | Usage |
|-------|-----|-------|
| Primary Blue | `#3498db` | Links, primary actions, accents |
| Dark Gray | `#2c3e50` | Headers, important text |
| Success Green | `#27ae60` | Success messages, low severity |
| Warning Orange | `#f39c12` | Medium severity, warnings |
| Danger Red | `#e74c3c` | High severity, errors |

### Neutral Colors

| Color | Hex | Usage |
|-------|-----|-------|
| Gray 50 | `#f8f9fa` | Backgrounds |
| Gray 100 | `#f0f0f0` | Subtle backgrounds |
| Gray 200 | `#e0e0e0` | Borders |
| Gray 400 | `#999` | Secondary text |
| Gray 600 | `#333` | Body text |

### Semantic Colors
```css
--success-color: #27ae60   /* Green for success */
--warning-color: #f39c12   /* Orange for warnings */
--danger-color: #e74c3c    /* Red for errors/danger */
--info-color: #3498db      /* Blue for information */
```

## Typography

### Font Stack
```css
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto',
  'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', sans-serif;
```

**Why this stack:**
- Native to each OS (looks familiar to users)
- Fast loading (no web fonts to download)
- Excellent readability

### Heading Sizes

| Element | Size | Usage |
|---------|------|-------|
| h1 | 2.5rem (40px) | Page title |
| h2 | 2rem (32px) | Section headers |
| h3 | 1.5rem (24px) | Subsection headers |
| h4 | 1.25rem (20px) | Card titles |
| Body | 1rem (16px) | Default text |

### Font Weights

- **400** (normal) - Body text
- **600** (semibold) - Labels, emphasis
- **700** (bold) - Headings

## Spacing Scale

Consistent spacing using 8px grid:
```css
--spacing-xs: 4px    /* 0.25rem */
--spacing-sm: 8px    /* 0.5rem */
--spacing-md: 16px   /* 1rem */
--spacing-lg: 24px   /* 1.5rem */
--spacing-xl: 32px   /* 2rem */
```

**Usage:**
- `xs`: Between related items
- `sm`: Between form fields
- `md`: Between sections
- `lg`: Between major components
- `xl`: Page margins

## Layout

### Two-Column Dashboard
```
┌─────────────────────────────────────────┐
│           Header (Full Width)           │
├──────────────┬──────────────────────────┤
│              │                          │
│  Left (1/3)  │      Right (2/3)        │
│              │                          │
│  - Forms     │   - Data Table          │
│  - Filters   │   - Results             │
│  - Actions   │   - Details             │
│              │                          │
└──────────────┴──────────────────────────┘
│           Footer (Full Width)           │
└─────────────────────────────────────────┘
```

**Ratio:** 1:2 (left gets 1/3, right gets 2/3)

**Responsive:** Stacks vertically on screens < 1024px

### Container Widths
```css
.app-main {
    max-width: 1400px;    /* Maximum content width */
    margin: 0 auto;       /* Center horizontally */
}
```

**Why limit width:**
- Lines of text shouldn't be too wide (hard to read)
- Professional apps don't use full screen on large displays

## Components

### Buttons
```css
.btn-primary {
    background: #3498db;   /* Blue */
    color: white;
    padding: 12px 24px;
    border-radius: 6px;
}

.btn-secondary {
    background: #ecf0f1;   /* Light gray */
    color: #2c3e50;
}

.btn-danger {
    background: #e74c3c;   /* Red */
    color: white;
}
```

### Cards
```css
.card {
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    padding: 24px;
}
```

### Badges
```css
.severity-high {
    background: #e74c3c;   /* Red */
    color: white;
    padding: 4px 10px;
    border-radius: 4px;
}
```

## Shadows
```css
--shadow-sm: 0 2px 4px rgba(0, 0, 0, 0.1);    /* Subtle */
--shadow-md: 0 2px 8px rgba(0, 0, 0, 0.1);    /* Medium */
--shadow-lg: 0 4px 12px rgba(0, 0, 0, 0.15);  /* Strong */
```

**Usage:**
- sm: Cards at rest
- md: Raised cards, panels
- lg: Modals, important elements

## Animations

### Transitions
```css
transition: all 0.2s ease;  /* Smooth property changes */
```

**Use on:**
- Button hover states
- Link colors
- Border colors
- Background colors

### Keyframe Animations
```css
@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

@keyframes slideIn {
    from { transform: translateX(100%); }
    to { transform: translateX(0); }
}
```

## Responsive Breakpoints
```css
/* Mobile */
@media (max-width: 768px) { }

/* Tablet */
@media (max-width: 1024px) { }

/* Desktop */
@media (min-width: 1400px) { }
```

## Accessibility

### Focus States
```css
*:focus-visible {
    outline: 2px solid #3498db;
    outline-offset: 2px;
}
```

### Color Contrast

All text meets WCAG AA standards:
- Body text: 4.5:1 contrast ratio minimum
- Headings: 4.5:1 contrast ratio minimum
- Interactive elements: 3:1 contrast ratio minimum

### Keyboard Navigation

- Tab through all interactive elements
- ESC closes panels
- Enter submits forms
- Arrow keys navigate (where applicable)

## Best Practices

✅ Use CSS variables for consistency  
✅ Mobile-first approach  
✅ Flexbox for layouts  
✅ 8px spacing grid  
✅ System fonts (fast loading)  
✅ Smooth transitions (0.2s)  
✅ Accessible focus states  

❌ Don't use fixed pixels for responsive elements  
❌ Don't use !important (indicates bad specificity)  
❌ Don't inline all styles (use CSS files)  
❌ Don't forget mobile testing  

---

*Design system established: Day 28*