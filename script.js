(() => {
  'use strict';
  document.documentElement.classList.add('js');
  const toggle = document.querySelector('.theme-toggle');
  const systemTheme = window.matchMedia('(prefers-color-scheme: dark)');
  const currentTheme = () => document.documentElement.dataset.theme || (systemTheme.matches ? 'dark' : 'light');
  function updateThemeControl() {
    const dark = currentTheme() === 'dark';
    toggle?.setAttribute('aria-label', `Switch to ${dark ? 'light' : 'dark'} mode`);
    if (toggle) toggle.querySelector('.theme-icon').textContent = dark ? '☀' : '☾';
    document.querySelector('meta[name="theme-color"]')?.setAttribute('content', dark ? '#111620' : '#f8f9fc');
  }
  if (toggle) {
    toggle.hidden = false;
    toggle.addEventListener('click', () => {
      const next = currentTheme() === 'dark' ? 'light' : 'dark';
      document.documentElement.dataset.theme = next;
      try { localStorage.setItem('portfolio-theme', next); } catch { /* Optional persistence. */ }
      updateThemeControl();
    });
    updateThemeControl();
    systemTheme.addEventListener('change', updateThemeControl);
  }
  const menu = document.querySelector('.menu-toggle');
  const nav = document.querySelector('#main-nav');
  function closeMenu(returnFocus = false) {
    nav?.classList.remove('is-open');
    menu?.setAttribute('aria-expanded', 'false');
    if (returnFocus) menu?.focus();
  }
  if (menu && nav) {
    menu.hidden = false;
    menu.addEventListener('click', () => {
      const open = menu.getAttribute('aria-expanded') !== 'true';
      menu.setAttribute('aria-expanded', String(open));
      nav.classList.toggle('is-open', open);
    });
    nav.addEventListener('click', event => {
      const link = event.target.closest('a[href^="#"]');
      if (!link) return;
      closeMenu();
      // Transfer focus out of the collapsed mobile menu to the destination.
      const destination = document.querySelector(link.getAttribute('href'));
      if (destination) {
        destination.setAttribute('tabindex', '-1');
        destination.focus({ preventScroll: true });
      }
    });
    document.addEventListener('keydown', event => {
      if (event.key === 'Escape' && menu.getAttribute('aria-expanded') === 'true') closeMenu(true);
    });
    window.matchMedia('(min-width: 601px)').addEventListener('change', () => closeMenu());
  }
  const portrait = document.querySelector('#profile-photo');
  if (portrait) {
    const onFailure = () => { portrait.hidden = true; };
    portrait.addEventListener('error', onFailure);
    if (portrait.complete && !portrait.naturalWidth) onFailure();
  }
  const year = document.querySelector('#copyright-year');
  if (year) year.textContent = String(new Date().getFullYear());
  // Open the privacy disclosure when following the form/footer link.
  document.querySelectorAll('a[href="#privacy-notice"]').forEach(link => link.addEventListener('click', () => {
    const detail = document.querySelector('#privacy-notice details');
    if (detail) detail.open = true;
  }));
})();

// Progressive glass interaction: native pointers and content stay usable without effects.
(() => {
  const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
  const finePointer = matchMedia('(hover: hover) and (pointer: fine)');
  const surfaces = document.querySelectorAll('.project-card, .certificate, .inquiry-form, .portrait-frame, .floating-note');
  surfaces.forEach(surface => {
    surface.classList.add('liquid-surface');
    let frame = 0;
    surface.addEventListener('pointermove', event => {
      if (reducedMotion.matches || !finePointer.matches || event.pointerType === 'touch') return;
      cancelAnimationFrame(frame);
      frame = requestAnimationFrame(() => {
        const rect = surface.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        surface.style.setProperty('--pointer-x', `${x}px`);
        surface.style.setProperty('--pointer-y', `${y}px`);
        surface.classList.add('is-hovered');
        if (surface.classList.contains('portrait-frame')) {
          surface.style.setProperty('--tilt-x', `${(0.5 - y / rect.height) * 4}deg`);
          surface.style.setProperty('--tilt-y', `${(x / rect.width - 0.5) * 4}deg`);
        }
      });
    });
    function reset() {
      cancelAnimationFrame(frame);
      surface.classList.remove('is-hovered');
      surface.style.removeProperty('--tilt-x');
      surface.style.removeProperty('--tilt-y');
    }
    surface.addEventListener('pointerleave', reset);
    reducedMotion.addEventListener('change', reset);
  });
  if (!('IntersectionObserver' in window)) return;
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      if (!reducedMotion.matches) entry.target.classList.add('reveal-visible');
      observer.unobserve(entry.target);
    });
  }, { threshold: 0.08 });
  document.querySelectorAll('.section-heading, .project-card, .research-row, .certificate, .about-grid, .contact-intro').forEach((element, index) => {
    element.style.setProperty('--reveal-delay', `${Math.min(index % 3, 2) * 55}ms`);
    observer.observe(element);
  });
})();
