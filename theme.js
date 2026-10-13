// Apply only a saved preference before paint; CSS handles the system default.
try {
  const theme = localStorage.getItem('portfolio-theme');
  if (theme === 'light' || theme === 'dark') document.documentElement.dataset.theme = theme;
} catch { /* Storage may be unavailable; the system preference still works. */ }
