# NACPAC — Web Project Context

The single source of truth for the nacpac.in website. Update this file as the strategy evolves so future sessions don't waste cycles re-deriving things.

---

## What NACPAC is

An in-house print studio in India selling **packaging accessories to small D2C product makers**. Differentiator: **no MOQ**, ₹399 minimum order value. Customer can order as few as 25 pieces, mix any designs, mix any materials.

**Name origin:** *knack + pack* — "an itch to pack." The dropped K's mirror the dropped MOQ. This is the brand's single best asset and should be visible everywhere (in spirit, not always as text).

---

## Who buys (target audience)

First-time D2C product makers, 18–35:

- **Candle makers** (need branded jar labels)
- **Soap makers** (waterproof product labels)
- **Food D2C founders** (FSSAI-aware labels — chocolates, honey, snacks, ghee)
- **Small online sellers** (thank-you stickers, seal stickers, inserts)

They are **not**: factories, large brands, Meesho sellers at scale, or anyone who can absorb a 500-piece MOQ. The site is built for someone with a Shopify store and 50–500 orders per month, possibly fewer.

**Mental model:** the candle-maker who has never bought packaging before. Every copy decision is tested against *"would she understand this in 3 seconds?"*

---

## Brand identity

### Colours

| Token       | Hex       | Use                                 |
|-------------|-----------|-------------------------------------|
| indigo      | `#29266c` | primary text, dark backgrounds      |
| purple      | `#5a3493` | secondary, brand accent             |
| lavender    | `#dccee6` | soft backgrounds, pills             |
| gold        | `#f5b11b` | mascot body, hover yellows          |
| yellow      | `#fdd223` | primary CTA fill                    |
| yellow-pale | `#fee17a` | soft accent backgrounds             |
| paper       | `#fdfbf6` | warm white page background          |

Never pure white anywhere. Indigo is the anchor; yellow is the accent; purple is the secondary; lavender for softness.

### Typography

- **Display:** Fredoka (rounded, friendly, lowercase-friendly)
- **Body:** Plus Jakarta Sans
- **Hand:** Caveat (for one-off script accents)

The brand wordmark is hand-drawn lowercase chunky sans — keep that organic, friendly feel everywhere.

### Voice

> Fun and proving a point. Welcoming. Plain-spoken. Never corporate.

The brand is *welcoming new entrepreneurs into the market*. Speak to someone who's nervous about their first big purchase, not someone running a procurement department.

### Mascot

A yellow tape-roll character with eyes, arms, sneakers, and a pointing hand. Source: `ai file.ai` extracted to `web/mascot.png`. Used as:

1. The floating widget at bottom-right (persistent across the site)
2. The brand mark in the nav (small)

The widget is **interactive but never idle-shaky**:

- Tracks the cursor (leans toward it)
- Reacts to scroll (brief lean + lift, then settles)
- Triggers a per-section gesture on scroll-in (bounce / point / wave / spin)
- Click opens a context-aware speech bubble

---

## Customer language rules (non-negotiable)

**Never use acronyms in customer-facing copy.** Specifically:

- ❌ "MOV ₹399" as a hero element
- ✅ "₹399 to start. Mix any designs."
- ❌ "MOQ" as a struck-through term in a headline
- ✅ "~~500-piece minimums~~. 25 to start." — strike the *number*, not the acronym

The strikethrough motif is brand-correct (NACPAC drops things: letters, minimums, friction) — but always apply it to a thing the customer already understands. Numbers work. Acronyms don't.

Internal docs / configurator labels / FAQ may use "MOV" if needed — but always spelled out alongside.

---

## Product v0 — Stickers only

We're shipping **stickers first** to learn the funnel (upload flow, proofing, fulfilment, repeat) before adding more products.

### Materials (4)

1. **Matte Vinyl** — workhorse for soap, candles, jars
2. **Optical / Clear** — transparent base, glass-product feel
3. **Holographic** — Instagram-bait, merch, drops
4. **Silver Chrome** — premium, beauty, boutique

Sample pack contains one of each, ₹129 inclusive of shipping. Credits toward first order over ₹399.

### Production

- Digital UV print + digital cutting (low setup cost per design — makes MOV viable)
- In-house. Fast iteration on proofs.
- Lowest piece quantity: 25.
- Minimum spend: ₹399.

### Roadmap (next 2 months)

- **July** — Thank-you cards
- **August** — Hang tags
- **Later** — Launch Kit bundle (stickers + cards + tags)
- **Killed** — Wallpapers, NTR rolls (wrong audience), coasters (under review — doesn't fit the unboxing-inserts story)

Stickers/cards/tags share the same flat-print production and the same buyer. Repeat purchase across the family is the real economic engine — single-sticker AOV is too low.

---

## Strategic decisions made

1. **Single product launch (stickers)** — to learn the ordering flow, not test the brand thesis. The thesis test comes when products 2 & 3 ship.
2. **E-commerce only** — no WhatsApp / DM order channel for v0. Site has to do the convincing alone. Needs session-replay tooling (Clarity / Hotjar) from day 1.
3. **Upfront payment** — kills RTO risk. The active risks are refund requests and bad reviews from poor proofs, both downstream of artwork intake.
4. **Two design tiers (flat fees)** — Quick fix and Full design. Never hourly. Customer needs to know the price before committing.
5. **Sample pack at ₹129 inclusive** — hesitation killer, near-cost. Credits to first order ≥ ₹399.
6. **Mascot as widget, not hero centrepiece** — persistent personality across sections, doesn't compete with product imagery in hero.

---

## Site structure (current)

`web/ideation.html` is the v0 mockup. Sections:

1. Sticky nav with mascot brand mark
2. Hero — sticker stack on right, headline copy on left
3. Marquee strip — indigo background with brand statements
4. Materials grid — 4 cards (Vinyl / Optical / Hologram / Chrome)
5. Sample pack feature block — dark indigo, ₹129 push
6. How it works — 3 steps (upload → preview cut line → ship)
7. Coming soon — cards/tags teaser + email capture
8. Footer

The floating mascot widget lives fixed bottom-right and persists across all sections.

---

## Cut-line auto-generation — planned build

This is the operational moat. Most first-time buyers will upload a PNG without a cut line and not understand why we email them back. Plan:

- **Phase 1** (~2 weeks) — PNG with transparency only. Server-side: Sharp + potrace. Auto-generate cut path, expand 3mm for bleed, show customer a preview before they pay.
- **Phase 2** (~month 2) — JPG / opaque background support via `rembg` (U2-Net model).
- **Phase 3** (ongoing) — manual fallback queue for edge cases (hair, photo composites, thin strokes).

Non-negotiable: customer sees and approves the cut-line preview *before* paying. Eliminates 90% of "this isn't what I expected" refund requests.

---

## Food D2C — pending honest decision

Food labels need:
1. Food-safe adhesive (direct-contact vs. non-direct standards)
2. FSSAI-compliant label template guidance (required fields, font sizes, allergen warnings)
3. Batch-consistency commitment across reorders

If yes to all three, food D2C is a wedge no one in India owns. If aspirational, **don't put food in marketing yet** — over-promising to this audience kills trust fast.

---

## Files in this folder

- `index.html`, `main.js`, `styles.css` — original brutalist landing (kept, may be deprecated)
- `ideation.html` — current v0 with mascot widget, ideation visuals
- `mascot.png` — extracted from `Downloads/ai file.ai`, ~408 KB
- `mascot-src/` — working files for mascot extraction (can be cleaned up)
- `nacpac-web-context.txt` — older context for the brutalist landing
- `nacpac.md` — this file

---

## What's still open

- Hero copy refresh — replace MOV/MOQ jargon with plain-number copy (see customer language rules above)
- Cut-line API + UI build
- Food D2C honesty decision (above)
- Configurator / PDP page design
- Real product photography (or commit to illustration-only forever)
- Real contact info (phone, WhatsApp, email — currently placeholders)
- Domain, hosting (Firebase Hosting natural given existing setup), analytics
- Mobile behaviour for the mascot widget (no cursor → only scroll + tap; needs review)

When picking the next thing to build, default order: (a) fix hero copy → (b) configurator/PDP → (c) cut-line build → (d) food D2C decision.
