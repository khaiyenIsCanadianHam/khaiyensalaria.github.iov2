# Validation — October 13, 2026

The static portfolio was tested locally at its GitHub Pages project subpath using Python Playwright and installed Chromium **154.0.8037.57**. The website itself requires no dependency installation or build.

| Check | Result |
| --- | --- |
| Responsive layout | **Pass:** 320, 375, 600, 768, 1024, 1440, and 1920 CSS pixels in both light and dark themes. Document and body widths never exceeded the viewport. |
| Automated accessibility | **Pass:** axe-core **4.10.3**, WCAG 2 A/AA and 2.1 AA tags, **zero violations in all 14 viewport/theme combinations**, after transitions settled. |
| Navigation and focus | **Pass:** mobile menu opens with Enter/Space; Escape closes it and returns focus; following a menu link focuses its destination; resizing to desktop resets menu state. Skip link is visible on keyboard focus. Privacy links open the disclosure. |
| Themes | **Pass:** system preference updates the theme control; explicit selection overrides the system and persists across reload. |
| Glass effects | **Pass:** pointer highlights and portrait tilt activate on fine-pointer hover and reset on leave. Reduced motion disables smooth scrolling, tilt, transitions, and reveal animation; reduced transparency removes header blur and reflections. |
| Local assets | **Pass:** 20 homepage assets/metadata resources return HTTP 200, including CSS, scripts, favicon, project image, social preview, sitemap, robots file, and all seven PDFs. PDF responses have valid PDF signatures. All in-page link targets exist and IDs are unique. |
| JavaScript disabled | **Pass:** at 320px in system dark mode, navigation, portfolio content, all four form sections, and the email fallback remain visible without horizontal overflow. Enhancement buttons remain hidden. |
| Image failure | **Pass:** blocking the local portrait request reveals the initials fallback without breaking layout. |
| Missing pages | **Pass locally:** missing nested path returns 404. Simulating GitHub Pages serving the custom `404.html` at that path loads its stylesheet and returns visitors to the project homepage. |
| Browser errors | **Pass:** no uncaught JavaScript errors in the UI smoke run. |
| Inquiry form | **Pass:** the separate `tests/form_smoke.py` run passed all five groups with mocked provider responses; no live inquiry was submitted. |
| Static validation | **Pass:** JavaScript syntax, anchors, IDs, local asset references, JSON-LD, and XML checks. |

The initial review found a redundant desktop menu button and insufficient contrast in the light-theme form step numbers. Both were fixed before the final passing run. Mobile and desktop screenshots were saved outside the repository at `/tmp/portfolio-{light,dark}-{375,1440}.png`; the no-JavaScript capture is `/tmp/portfolio-nojs-320.png`.

## Reproduce

Run the static server from the parent of this checkout so the project subpath is preserved:

```bash
python3 -m http.server 8000 --bind 127.0.0.1 --directory /workspace
```

In a second terminal, from this repository:

```bash
python tests/site_smoke.py
python tests/form_smoke.py --base-url http://127.0.0.1:8000/khaiyensalaria.github.iov2/
```

The optional accessibility audit uses an externally supplied axe-core file. The reported run used the pinned distribution downloaded over verified HTTPS from the allowed jsDelivr host:

```bash
curl --fail --location --silent --show-error https://cdn.jsdelivr.net/npm/axe-core@4.10.3/axe.min.js --output /tmp/portfolio-axe.min.js
python tests/site_smoke.py --axe /tmp/portfolio-axe.min.js
```

The UI test accepts `--url`, `--chromium`, and `--screenshots` overrides. Form tests mock provider responses; neither test submits a live inquiry or sends email.

## Scope and remaining checks

These are Chromium viewport and behavior checks, not testing on physical iOS/Android devices or Safari/Firefox. Automated accessibility results do not replace assistive-technology and user testing. Lighthouse was not run. GitHub Pages deployment and its actual 404 response still need checking after publication. External social pages were not navigated by this test. The original owner-supplied portrait is now a local JPEG and its normal rendering and image-load fallback have been tested. Real inquiry delivery requires the owner's Web3Forms public access key and a successful mailbox receipt test; mocked responses do not establish delivery.

## Project mockup update

After replacing all four project previews with generated laptop mockups, the complete UI suite passed again at 320, 375, 600, 768, 1024, 1440, and 1920 CSS pixels in both themes, with zero automated axe violations. All four local WebP images loaded at 1536 × 1024. Their 3:2 framing, descriptive alt text, lazy loading, and mockup/sample-data captions were verified. Each encoded image is approximately 90–104 KB. No inquiry code changed. The portrait was later supplied as a downloadable archive and installed unchanged; no AI-redrawn portrait was installed.

## Original portrait update

The original `pfp.jpg` from the owner’s `pfp.zip` was copied byte-for-byte to `assets/images/profile.jpg`. A browser check confirmed its 460 × 460 intrinsic dimensions, normal rendering at 375px, and the monogram fallback when its request is blocked. The external avatar dependency and the computer-specific file path were removed.

The complete UI suite also passed again with the local portrait: all 14 viewport/theme combinations, zero automated axe violations, 20 local resources, keyboard navigation, theme behavior, reduced-motion behavior, and the no-JavaScript fallback. Keyboard-order checks now use a fresh document rather than reloading an already focused fragment URL.
