# Overlytics Landing Page — Concept & Instructions

## Overview

This directory contains the landing page concept for **Overlytics**, a Django web app for tracking Overleaf (LaTeX) writing projects. The landing page is a standalone static HTML file (`index.html`) requiring no build step.

---

## Tagline Concepts

Three candidates, ranging from data-forward to emotionally resonant:

### 1. "Understand your research velocity" *(recommended)*
**Tone:** Analytical, empowering
**Why it works:** "Velocity" is a scientific term that resonates with the target audience (researchers, PhD students). It frames writing as measurable progress — not just effort. Strong and memorable.

### 2. "Track your LaTeX. See your momentum."
**Tone:** Direct, action-oriented
**Why it works:** Two short imperatives that speak to the core loop. "Momentum" carries a motivational charge without being cheesy. Good for shorter CTAs or subheadings.

### 3. "Your thesis, measured."
**Tone:** Quiet confidence, minimal
**Why it works:** Extremely concise. Implies precision and calm control. Best as a closing tagline (used in the final CTA section) rather than the hero headline.

**Recommendation:** Use **#1** as the primary hero headline, **#3** as the closing CTA tagline, and **#2** as a secondary subheading or social media copy.

---

## Page Sections

| # | Section | Purpose |
|---|---------|---------|
| 1 | **Nav** | Fixed navbar with logo + links + CTA button |
| 2 | **Hero** | Primary headline, subtitle, CTA, mock dashboard card |
| 3 | **Metrics strip** | Quick social proof numbers (words tracked, metrics, sync) |
| 4 | **Features (4 cards)** | Velocity tracking, deep LaTeX metrics, group collab, Git sync |
| 5 | **How it works** | 3-step numbered flow with visual accent block |
| 6 | **Audience callout** | Dark forest section targeting PhD students, labs, paper authors |
| 7 | **Final CTA** | Closing tagline + register link |
| 8 | **Footer** | Logo, copyright, legal links |

---

## Design Direction

**Aesthetic:** Editorial/academic-meets-modern-data dashboard
**Inspiration:** The warmth of a well-typeset journal combined with the clarity of an analytics tool

### Color Palette
| Token | Hex | Usage |
|-------|-----|-------|
| `forest` | `#344945` | Primary text, buttons, headers, sidebar chrome |
| `cream` | `#F7F5F1` | Page background (warm off-white) |
| `beige` | `#E0DCD1` | Borders, dividers |
| `sage` | `#D5E3E8` | Feature card accent, badge backgrounds |
| `wheat` | `#E4E3BC` | Feature card accent, warning badges |

### Typography
- **Display/headings:** Playfair Display (serif) — gives academic gravitas and differentiates from generic SaaS
- **Body/UI:** Inter — clean and legible for data-heavy UI
- **Pairing rationale:** The serif/sans-serif contrast mirrors the tension between traditional academic writing and modern data tooling — which is exactly what Overlytics bridges

### Key Visual Decisions
- **Mock dashboard in hero:** Shows a realistic-looking stats card with animated SVG chart line drawing in, floating accent cards with "+2,841 words today" and sync status, and a fake projects list
- **Gentle float animation:** The dashboard card floats up and down subtly — gives life without being distracting
- **Warm, not sterile:** Deliberately avoids the cold blue/grey palette of generic SaaS tools. The cream/forest combination reads as trustworthy and intellectually serious
- **Serif display font:** Sets Overlytics apart from every other analytics tool. Signals "we understand academia"

---

## Integration into Django

To serve this as a real landing page from the Django app:

### Option A: Static file (simplest)
1. Move `index.html` into `templates/landing/index.html`
2. Create a simple view in a new app or `overlytics/urls.py`:
   ```python
   from django.views.generic import TemplateView
   urlpatterns = [
       path('', TemplateView.as_view(template_name='landing/index.html'), name='landing'),
       # ... existing urls
   ]
   ```
3. Update `templates/landing/index.html` to use `{% url 'account_signup' %}` for the CTA buttons

### Option B: Redirect authenticated users
```python
from django.shortcuts import redirect
from django.views.generic import TemplateView

class LandingView(TemplateView):
    template_name = 'landing/index.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)
```

### CTA Button URLs to wire up
- "Get Started Free" → `{% url 'account_signup' %}`  (or your registration URL)
- "See how it works" → `#how-it-works` (stays as anchor)
- Nav "Get Started Free" → same registration URL
- "Start tracking for free" → registration URL
- Footer legal links → create `/privacy/` and `/terms/` pages as needed

---

## Copy Variants

### Hero subtitle options
- *Current:* "Overlytics connects to your Overleaf projects and tracks your writing progress — words, pages, citations, and more — so you always know where you stand."
- *Alternative A:* "Stop guessing how much you've written. Overlytics syncs with Overleaf and turns your LaTeX into progress — tracked automatically, shown beautifully."
- *Alternative B (shorter):* "Connect your Overleaf projects. Watch your research grow. Automatic sync, zero manual effort."

### Feature headline variants
- "Everything your thesis needs, nothing it doesn't" *(current)*
- "Your complete research writing dashboard"
- "Five metrics. One dashboard. Total clarity."

---

## Files in this directory

```
landing/
├── CONCEPT.md      ← this file
└── index.html      ← standalone HTML landing page (open in browser directly)
```

The `index.html` file is fully self-contained — open it directly in a browser to preview. No build step, no server needed.
