class CustomNavbar extends HTMLElement {
    connectedCallback() {
        this.attachShadow({ mode: 'open' });
        this.shadowRoot.innerHTML = `
            <style>
                :host { display: block; }
                .header { position: sticky; top: 0; z-index: 50; background: #0b1b2b; box-shadow: 0 2px 10px rgba(0,0,0,0.08); }
                .bar { max-width: 1200px; margin: 0 auto; padding: 12px 16px; display: flex; align-items: center; justify-content: space-between; }
                .logo { display: flex; align-items: center; gap: 10px; text-decoration: none; }
                .logo__mark { font-size: 20px; }
                .logo__text { color: #fff; font-weight: 700; font-size: 18px; }
                .actions { display: flex; align-items: center; gap: 12px; }
                .btn { border: none; cursor: pointer; border-radius: 8px; padding: 10px 14px; font-weight: 600; }
                .btn--primary { background: #06b6d4; color: #0b1b2b; }
                .btn--ghost { background: transparent; color: #cbd5e1; }
                .link { color: #cbd5e1; text-decoration: none; }
                .menu { display: none; background: transparent; color: #cbd5e1; font-size: 22px; }
                @media (max-width: 768px) { .hide-sm { display:none; } .menu { display:block; } }
                .mobile { display: none; background: #10233a; border-top: 1px solid rgba(255,255,255,0.08); }
                .mobile.open { display: block; }
                .mobile a { display:block; color:#e2e8f0; text-decoration:none; padding:12px 16px; }
                .mobile a:hover { background: rgba(255,255,255,0.06); }
            </style>
            <nav class="header" role="navigation" aria-label="Main">
                <div class="bar">
                    <a href="/" class="logo" aria-label="Homepage">
                        <span class="logo__mark">🚆</span>
                        <span class="logo__text">PakRail Express</span>
                    </a>
                    <div class="actions">
                        <button class="btn btn--ghost hide-sm" id="openSearch" aria-label="Open search">Search</button>
                        <a href="/bookings" class="link hide-sm">My Bookings</a>
                        <button class="btn btn--primary" id="openAuth">Sign In</button>
                        <button class="menu" id="mobileMenuBtn" aria-expanded="false" aria-controls="mobileNav">☰</button>
                    </div>
                </div>
                <div class="mobile" id="mobileNav" aria-hidden="true">
                    <a href="/">Home</a>
                    <a href="/search">Search Trains</a>
                    <a href="/bookings">My Bookings</a>
                    <button id="openAuthMobile" style="background:transparent;color:#e2e8f0;border:none;text-align:left;padding:12px 16px;">Sign In</button>
                </div>
            </nav>
        `;
    }
}

customElements.define('custom-navbar', CustomNavbar);