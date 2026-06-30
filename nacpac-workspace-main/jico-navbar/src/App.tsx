import './App.css'

// ─── Design Tokens ───────────────────────────────────────────────
const C = {
  charcoal:    '#2C2C2A',
  linen:       '#F1EFE8',
  linenWash:   '#FAF8F4',
  pressedFelt: '#D3D1C7',
  amber:       '#BA7517',
  amberDark:   '#9A6010',
  amberLight:  '#F5E6C8',
  sage:        '#6B7F6E',
  terracotta:  '#C97B5A',
  brass:       '#9A7B3A',
  white:       '#FFFFFF',
}

const navItems = ['Statement Walls','Quiet Walls','Kids Room','The Light','Samples']

const categories = [
  { label: 'Statement Walls', sub: 'Orbit Puzzle · Designer Edition · The Dado', accent: C.amber,      img: '/hero.jpg' },
  { label: 'Quiet Walls',     sub: 'Groove Panels · Engraved Texture',           accent: C.sage,       img: '/quiet-1.jpg' },
  { label: 'Kids Room',       sub: 'Nursery · Games · Cartoons',                 accent: C.terracotta, img: null },
  { label: 'The Light',       sub: 'Felt Pendant Lamps',                         accent: C.brass,      img: null },
  { label: 'Samples',         sub: 'Try before you commit',                      accent: C.pressedFelt,img: null },
]

// ─── Icons ───────────────────────────────────────────────────────
const CartIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke={C.charcoal} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M6 2L3 6v14a2 2 0 002 2h14a2 2 0 002-2V6l-3-4z"/><line x1="3" y1="6" x2="21" y2="6"/>
    <path d="M16 10a4 4 0 01-8 0"/>
  </svg>
)
const SearchIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke={C.charcoal} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
  </svg>
)
const ArrowRight = ({ color = C.charcoal }: { color?: string }) => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/>
  </svg>
)

// ─── App ─────────────────────────────────────────────────────────
export default function App() {
  return (
    <div style={{ backgroundColor: C.linen, fontFamily: 'inherit', color: C.charcoal }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;1,400;1,500&family=DM+Sans:wght@300;400;500&display=swap');
        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
        body { background: ${C.linen}; }
        .nav-link:hover { color: ${C.amber} !important; }
        .cat-card:hover .cat-arrow { opacity: 1 !important; transform: translateX(4px) !important; }
        .cat-card:hover { box-shadow: 0 8px 32px rgba(44,44,42,0.10) !important; }
        .cta-btn:hover { background: ${C.amberDark} !important; }
        .cta-outline:hover { background: ${C.amberLight} !important; }
      `}</style>

      {/* ── Announcement Bar ── */}
      <div style={{ background: C.charcoal, color: C.linen, textAlign: 'center', padding: '9px 24px', fontSize: '11px', letterSpacing: '0.14em', fontFamily: "'DM Sans', sans-serif" }}>
        Free shipping above ₹4,999 &nbsp;·&nbsp; Renter-safe, no drill &nbsp;·&nbsp; Ships flat, installs in minutes &nbsp;·&nbsp; 50% recycled PET felt
      </div>

      {/* ── Header ── */}
      <header style={{ background: C.linen, borderBottom: `1px solid ${C.pressedFelt}`, padding: '0 56px', position: 'sticky', top: 0, zIndex: 100 }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', paddingTop: '16px', paddingBottom: '4px' }}>
          <img src="/logo.png" alt="Jico Life" style={{ height: '48px', width: 'auto', mixBlendMode: 'multiply' }}/>
          <div style={{ display: 'flex', gap: '22px', alignItems: 'center' }}><SearchIcon/><CartIcon/></div>
        </div>
        <nav style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', paddingTop: '8px', paddingBottom: '14px' }}>
          {navItems.map((item, i) => (
            <span key={item} style={{ display: 'flex', alignItems: 'center' }}>
              <span className="nav-link" style={{ fontFamily: "'DM Sans', sans-serif", fontSize: '12.5px', fontWeight: 400, color: C.charcoal, letterSpacing: '0.07em', padding: '4px 16px', whiteSpace: 'nowrap', cursor: 'pointer', transition: 'color 0.2s' }}>{item}</span>
              {i < navItems.length - 1 && <span style={{ color: C.pressedFelt, fontSize: '12px' }}>·</span>}
            </span>
          ))}
        </nav>
      </header>

      {/* ── Hero ── */}
      <section style={{ display: 'flex', minHeight: '620px', overflow: 'hidden' }}>
        {/* Copy */}
        <div style={{ width: '42%', flexShrink: 0, background: C.linen, display: 'flex', flexDirection: 'column', justifyContent: 'center', padding: '72px 56px', gap: '22px' }}>
          <p style={{ fontFamily: "'DM Sans', sans-serif", fontSize: '10.5px', color: C.amber, letterSpacing: '0.22em', fontWeight: 500, textTransform: 'uppercase' }}>
            Acoustic Art Objects · Recycled PET Felt
          </p>
          <h1 style={{ fontFamily: "'Cormorant Garamond', serif", fontSize: '58px', fontWeight: 500, color: C.charcoal, lineHeight: 1.1, letterSpacing: '0.01em' }}>
            Your walls<br/>are working.<br/><em style={{ fontStyle: 'italic', fontWeight: 400 }}>Make them feel<br/>something too.</em>
          </h1>
          <p style={{ fontFamily: "'DM Sans', sans-serif", fontSize: '13.5px', color: C.charcoal, opacity: 0.5, fontWeight: 300, lineHeight: 1.8, maxWidth: '340px' }}>
            Wall art that absorbs sound. Renter-safe.<br/>Ships flat, installs in minutes.
          </p>
          <div style={{ display: 'flex', gap: '12px', marginTop: '6px' }}>
            <button className="cta-btn" style={{ padding: '14px 30px', background: C.amber, color: C.white, fontFamily: "'DM Sans', sans-serif", fontSize: '11px', letterSpacing: '0.16em', fontWeight: 500, border: 'none', cursor: 'pointer', transition: 'background 0.2s' }}>EXPLORE THE COLLECTION</button>
            <button className="cta-outline" style={{ padding: '14px 30px', border: `1px solid ${C.amber}`, color: C.amber, background: 'transparent', fontFamily: "'DM Sans', sans-serif", fontSize: '11px', letterSpacing: '0.16em', fontWeight: 400, cursor: 'pointer', transition: 'background 0.2s' }}>THE MATERIAL</button>
          </div>
          <p style={{ fontFamily: "'DM Sans', sans-serif", fontSize: '11px', color: C.charcoal, opacity: 0.35, letterSpacing: '0.06em' }}>
            0.9 NRC · 63% sound dampening · 50% recycled
          </p>
        </div>
        {/* Photo */}
        <div style={{ flex: 1, position: 'relative', overflow: 'hidden' }}>
          <img src="/hero.jpg" alt="Orbit Puzzle in a warm living room" style={{ width: '100%', height: '100%', objectFit: 'cover', objectPosition: 'center', display: 'block' }}/>
          <div style={{ position: 'absolute', inset: 0, left: 0, width: '80px', background: `linear-gradient(to right, ${C.linen}, transparent)`, pointerEvents: 'none' }}/>
        </div>
      </section>

      {/* ── Benefit Bar ── */}
      <div style={{ background: C.white, borderTop: `1px solid ${C.pressedFelt}`, borderBottom: `1px solid ${C.pressedFelt}`, display: 'flex', justifyContent: 'center', padding: '20px 0' }}>
        {[['0.9 NRC Rating','Absorbs 9 in 10 sound waves'],['Renter-Safe','No drill, no damage'],['50% Recycled','Made from PET felt'],['Ships Flat','Installs in minutes']].map(([t, s], i, arr) => (
          <div key={t} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '0 56px', borderRight: i < arr.length - 1 ? `1px solid ${C.pressedFelt}` : 'none', gap: '4px' }}>
            <span style={{ fontFamily: "'DM Sans', sans-serif", fontSize: '12px', fontWeight: 500, color: C.charcoal, letterSpacing: '0.08em' }}>{t}</span>
            <span style={{ fontFamily: "'DM Sans', sans-serif", fontSize: '11px', color: C.charcoal, opacity: 0.4, letterSpacing: '0.04em' }}>{s}</span>
          </div>
        ))}
      </div>

      {/* ── Categories ── */}
      <section style={{ background: C.linenWash, padding: '80px 56px' }}>
        <div style={{ marginBottom: '48px' }}>
          <p style={{ fontFamily: "'DM Sans', sans-serif", fontSize: '10.5px', color: C.amber, letterSpacing: '0.22em', fontWeight: 500, textTransform: 'uppercase', marginBottom: '12px' }}>Shop by intent</p>
          <h2 style={{ fontFamily: "'Cormorant Garamond', serif", fontSize: '42px', fontWeight: 500, color: C.charcoal, lineHeight: 1.15 }}>What does your room need?</h2>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '16px' }}>
          {categories.map(({ label, sub, accent, img }) => (
            <div key={label} className="cat-card" style={{ background: C.white, border: `1px solid ${C.pressedFelt}`, cursor: 'pointer', transition: 'box-shadow 0.25s', position: 'relative', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
              {/* Image or colour block */}
              <div style={{ height: '200px', overflow: 'hidden', position: 'relative', background: img ? 'transparent' : accent, opacity: img ? 1 : 0.15 }}>
                {img
                  ? <img src={img} alt={label} style={{ width: '100%', height: '100%', objectFit: 'cover', objectPosition: 'center', display: 'block' }}/>
                  : <div style={{ position: 'absolute', inset: 0, background: accent, opacity: 0.25 }}/>
                }
                {/* Accent top bar */}
                <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: '3px', background: accent }}/>
              </div>
              {/* Card body */}
              <div style={{ padding: '20px', flex: 1, display: 'flex', flexDirection: 'column', gap: '8px' }}>
                <p style={{ fontFamily: "'Cormorant Garamond', serif", fontSize: '20px', fontWeight: 500, color: C.charcoal, lineHeight: 1.2 }}>{label}</p>
                <p style={{ fontFamily: "'DM Sans', sans-serif", fontSize: '11px', color: C.charcoal, opacity: 0.45, letterSpacing: '0.04em', lineHeight: 1.6 }}>{sub}</p>
                <div style={{ marginTop: 'auto', paddingTop: '16px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <span style={{ fontFamily: "'DM Sans', sans-serif", fontSize: '11px', fontWeight: 500, color: accent, letterSpacing: '0.08em' }}>EXPLORE</span>
                  <span className="cat-arrow" style={{ opacity: 0, transform: 'translateX(-4px)', transition: 'all 0.2s' }}><ArrowRight color={accent}/></span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ── Statement Walls Feature ── */}
      <section style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', minHeight: '560px', overflow: 'hidden' }}>
        {/* Photo */}
        <div style={{ position: 'relative', overflow: 'hidden' }}>
          <img src="/orbit-2.jpg" alt="Statement Walls" style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block' }}/>
        </div>
        {/* Copy */}
        <div style={{ background: C.charcoal, display: 'flex', flexDirection: 'column', justifyContent: 'center', padding: '72px 64px', gap: '24px' }}>
          <p style={{ fontFamily: "'DM Sans', sans-serif", fontSize: '10.5px', color: C.amber, letterSpacing: '0.22em', fontWeight: 500, textTransform: 'uppercase' }}>Statement Walls</p>
          <h2 style={{ fontFamily: "'Cormorant Garamond', serif", fontSize: '48px', fontWeight: 500, color: C.linen, lineHeight: 1.15 }}>
            One system.<br/><em style={{ fontStyle: 'italic', fontWeight: 400 }}>Infinite walls.</em>
          </h2>
          <p style={{ fontFamily: "'DM Sans', sans-serif", fontSize: '13.5px', color: C.linen, opacity: 0.55, fontWeight: 300, lineHeight: 1.8, maxWidth: '360px' }}>
            8 geometric pieces. 3 colour palettes. Mix, rotate, compose your own rhythm. Bauhaus-inspired, acoustically engineered, renter-safe.
          </p>
          <div style={{ display: 'flex', gap: '12px', marginTop: '8px' }}>
            <button className="cta-btn" style={{ padding: '14px 30px', background: C.amber, color: C.white, fontFamily: "'DM Sans', sans-serif", fontSize: '11px', letterSpacing: '0.16em', fontWeight: 500, border: 'none', cursor: 'pointer', transition: 'background 0.2s' }}>SHOP ORBIT PUZZLE</button>
          </div>
          <div style={{ display: 'flex', gap: '24px', marginTop: '8px', paddingTop: '24px', borderTop: `1px solid rgba(211,209,199,0.2)` }}>
            {[['8','Geometric pieces'],['3','Colour palettes'],['∞','Compositions']].map(([n, l]) => (
              <div key={l}>
                <p style={{ fontFamily: "'Cormorant Garamond', serif", fontSize: '32px', fontWeight: 500, color: C.amber }}>{n}</p>
                <p style={{ fontFamily: "'DM Sans', sans-serif", fontSize: '11px', color: C.linen, opacity: 0.4, letterSpacing: '0.06em' }}>{l}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Quiet Walls Feature ── */}
      <section style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', minHeight: '520px', overflow: 'hidden' }}>
        {/* Copy */}
        <div style={{ background: C.linenWash, display: 'flex', flexDirection: 'column', justifyContent: 'center', padding: '72px 64px', gap: '24px' }}>
          <p style={{ fontFamily: "'DM Sans', sans-serif", fontSize: '10.5px', color: C.sage, letterSpacing: '0.22em', fontWeight: 500, textTransform: 'uppercase' }}>Quiet Walls</p>
          <h2 style={{ fontFamily: "'Cormorant Garamond', serif", fontSize: '48px', fontWeight: 500, color: C.charcoal, lineHeight: 1.15 }}>
            The pattern only<br/>appears in light.<br/><em style={{ fontStyle: 'italic', fontWeight: 400 }}>That's the point.</em>
          </h2>
          <p style={{ fontFamily: "'DM Sans', sans-serif", fontSize: '13.5px', color: C.charcoal, opacity: 0.5, fontWeight: 300, lineHeight: 1.8, maxWidth: '360px' }}>
            Embossed tone-on-tone acoustic panels. The engraving lives in shadow. Side-lit or directional natural light makes the texture come alive.
          </p>
          <button className="cta-btn" style={{ alignSelf: 'flex-start', padding: '14px 30px', background: C.sage, color: C.white, fontFamily: "'DM Sans', sans-serif", fontSize: '11px', letterSpacing: '0.16em', fontWeight: 500, border: 'none', cursor: 'pointer', transition: 'background 0.2s' }}>SHOP QUIET WALLS</button>
        </div>
        {/* Photo */}
        <div style={{ position: 'relative', overflow: 'hidden' }}>
          <img src="/quiet-2.jpg" alt="Quiet Walls" style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block' }}/>
        </div>
      </section>

      {/* ── The Dado Feature ── */}
      <section style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', minHeight: '520px', overflow: 'hidden' }}>
        {/* Photo */}
        <div style={{ position: 'relative', overflow: 'hidden' }}>
          <img src="/dado-2.jpg" alt="The Dado" style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block' }}/>
        </div>
        {/* Copy */}
        <div style={{ background: C.linen, display: 'flex', flexDirection: 'column', justifyContent: 'center', padding: '72px 64px', gap: '24px' }}>
          <p style={{ fontFamily: "'DM Sans', sans-serif", fontSize: '10.5px', color: C.amberDark, letterSpacing: '0.22em', fontWeight: 500, textTransform: 'uppercase' }}>Inside Statement Walls</p>
          <h2 style={{ fontFamily: "'Cormorant Garamond', serif", fontSize: '48px', fontWeight: 500, color: C.charcoal, lineHeight: 1.15 }}>
            The 18 inches<br/><em style={{ fontStyle: 'italic', fontWeight: 400 }}>that change a room.</em>
          </h2>
          <p style={{ fontFamily: "'DM Sans', sans-serif", fontSize: '13.5px', color: C.charcoal, opacity: 0.5, fontWeight: 300, lineHeight: 1.8, maxWidth: '360px' }}>
            Acoustic wainscoting at dado height. Wall to wall. 6 patterns named in Hindi and Sanskrit. The room transformer — for homeowners and long-lease renters.
          </p>
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            {['Vastu','Dhara','Mandala','Taru','Raga','Jaal'].map(p => (
              <span key={p} style={{ padding: '5px 12px', background: C.amberLight, fontFamily: "'DM Sans', sans-serif", fontSize: '10.5px', color: C.amberDark, letterSpacing: '0.08em' }}>{p}</span>
            ))}
          </div>
          <button className="cta-btn" style={{ alignSelf: 'flex-start', padding: '14px 30px', background: C.amber, color: C.white, fontFamily: "'DM Sans', sans-serif", fontSize: '11px', letterSpacing: '0.16em', fontWeight: 500, border: 'none', cursor: 'pointer', transition: 'background 0.2s' }}>EXPLORE THE DADO</button>
        </div>
      </section>

      {/* ── The Material Teaser ── */}
      <section style={{ background: C.charcoal, padding: '80px 56px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '48px' }}>
        <div style={{ maxWidth: '560px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <p style={{ fontFamily: "'DM Sans', sans-serif", fontSize: '10.5px', color: C.amber, letterSpacing: '0.22em', fontWeight: 500, textTransform: 'uppercase' }}>The Material</p>
          <h2 style={{ fontFamily: "'Cormorant Garamond', serif", fontSize: '42px', fontWeight: 500, color: C.linen, lineHeight: 1.2 }}>
            This isn't the felt<br/>from a craft store.
          </h2>
          <p style={{ fontFamily: "'DM Sans', sans-serif", fontSize: '13.5px', color: C.linen, opacity: 0.5, fontWeight: 300, lineHeight: 1.8 }}>
            Recycled PET, engineered to absorb — tested, certified, and designed to last. Every JICO product starts with the same material: 0.9 NRC, 63% sound dampening, 50% recycled plastic bottles, flame retardant, temperature regulating.
          </p>
          <button className="cta-outline" style={{ alignSelf: 'flex-start', padding: '14px 30px', border: `1px solid ${C.amber}`, color: C.amber, background: 'transparent', fontFamily: "'DM Sans', sans-serif", fontSize: '11px', letterSpacing: '0.16em', fontWeight: 400, cursor: 'pointer', transition: 'background 0.2s' }}>READ THE MATERIAL STORY</button>
        </div>
        {/* Specs grid */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', flexShrink: 0 }}>
          {[['0.9','NRC Rating'],['63%','Sound dampening'],['50%','Recycled content'],['Zero','Emissions']].map(([n, l]) => (
            <div key={l} style={{ padding: '28px', border: `1px solid rgba(211,209,199,0.15)`, display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <p style={{ fontFamily: "'Cormorant Garamond', serif", fontSize: '40px', fontWeight: 500, color: C.amber }}>{n}</p>
              <p style={{ fontFamily: "'DM Sans', sans-serif", fontSize: '11px', color: C.linen, opacity: 0.4, letterSpacing: '0.08em' }}>{l}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── Footer ── */}
      <footer style={{ background: C.charcoal, borderTop: `1px solid rgba(211,209,199,0.12)`, padding: '48px 56px 32px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr 1fr 1fr', gap: '48px', marginBottom: '48px' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <img src="/logo.png" alt="Jico Life" style={{ height: '40px', width: 'auto', mixBlendMode: 'screen', opacity: 0.9, alignSelf: 'flex-start' }}/>
            <p style={{ fontFamily: "'DM Sans', sans-serif", fontSize: '12px', color: C.linen, opacity: 0.4, lineHeight: 1.8, maxWidth: '260px' }}>Acoustic art objects made from recycled PET felt. Calm by design, alive by intention.</p>
          </div>
          {[
            ['Shop', ['Statement Walls','Quiet Walls','Kids Room','The Light','Samples']],
            ['Brand', ['The Material','Designer Edition','About JICO','Stockists']],
            ['Support', ['Shipping & Returns','Installation Guide','Contact Us','Commercial']],
          ].map(([heading, links]) => (
            <div key={heading as string} style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <p style={{ fontFamily: "'DM Sans', sans-serif", fontSize: '11px', fontWeight: 500, color: C.linen, letterSpacing: '0.12em', opacity: 0.6 }}>{heading as string}</p>
              {(links as string[]).map(link => (
                <p key={link} style={{ fontFamily: "'DM Sans', sans-serif", fontSize: '12px', color: C.linen, opacity: 0.35, cursor: 'pointer', letterSpacing: '0.04em' }}>{link}</p>
              ))}
            </div>
          ))}
        </div>
        <div style={{ borderTop: `1px solid rgba(211,209,199,0.12)`, paddingTop: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <p style={{ fontFamily: "'DM Sans', sans-serif", fontSize: '11px', color: C.linen, opacity: 0.25, letterSpacing: '0.06em' }}>© 2026 JICO Life. All rights reserved.</p>
          <p style={{ fontFamily: "'DM Sans', sans-serif", fontSize: '11px', color: C.linen, opacity: 0.25, letterSpacing: '0.06em' }}>Made in India · Shipped across India</p>
        </div>
      </footer>

    </div>
  )
}
