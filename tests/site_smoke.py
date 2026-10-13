"""Browser smoke checks; requires Python Playwright and an installed Chromium.

Serve /workspace on port 8000, then run:
  python tests/site_smoke.py --axe /tmp/portfolio-axe.min.js
The optional axe file is a separately downloaded axe-core distribution.
No live form submissions or external page navigations are made.
"""

import argparse
import json
import re
from pathlib import Path
from urllib.parse import urljoin, urlparse

from playwright.sync_api import expect, sync_playwright


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", "--base-url", dest="url", default="http://127.0.0.1:8000/khaiyensalaria.github.iov2/")
    parser.add_argument("--chromium", default="/usr/bin/chromium")
    parser.add_argument("--axe", type=Path)
    parser.add_argument("--screenshots", type=Path, default=Path("/tmp"))
    args = parser.parse_args()
    args.screenshots.mkdir(parents=True, exist_ok=True)
    results = {"viewports": [], "checks": [], "axe": "not requested"}
    errors = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path=args.chromium, args=["--no-sandbox"])
        context = browser.new_context(viewport={"width": 1440, "height": 1000}, color_scheme="light")
        # The remote avatar is unavailable in this environment: exercise its fallback.
        context.route("https://avatars.githubusercontent.com/**", lambda route: route.abort())
        page = context.new_page()
        page.on("pageerror", lambda error: errors.append(str(error)))
        assert page.goto(args.url, wait_until="networkidle").status == 200
        if args.axe:
            page.add_script_tag(path=str(args.axe))
            results["axe"] = []
        for theme in ("light", "dark"):
            page.evaluate("theme => document.documentElement.dataset.theme = theme", theme)
            for width in (320, 375, 600, 768, 1024, 1440, 1920):
                page.set_viewport_size({"width": width, "height": 1000})
                page.wait_for_timeout(850)  # Finish theme/reveal transitions before measuring.
                dimensions = page.evaluate("() => ({viewport: innerWidth, body: document.body.scrollWidth, html: document.documentElement.scrollWidth})")
                assert dimensions["body"] <= width and dimensions["html"] <= width, dimensions
                expect(page.locator(".menu-toggle")).to_be_visible() if width <= 600 else expect(page.locator(".menu-toggle")).to_be_hidden()
                results["viewports"].append({"theme": theme, **dimensions})
                if args.axe:
                    violations = page.evaluate("""async () => (await axe.run(document, {
                      runOnly: {type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21aa']}
                    })).violations.map(v => ({id: v.id, impact: v.impact, nodes: v.nodes.map(n => n.target)}))""")
                    assert not violations, (theme, width, violations)
                    results["axe"].append({"theme": theme, "width": width, "violations": 0})
                if width in (375, 1440):
                    page.screenshot(path=str(args.screenshots / f"portfolio-{theme}-{width}.png"), full_page=True)
        results["checks"].append("14 viewport/theme combinations: no horizontal overflow; responsive menu; optional axe")

        # Check real local resources rather than assuming successful HTML means a usable site.
        assets = page.evaluate("""() => [...new Set([...document.querySelectorAll('a[href], link[href], script[src], img[src]')]
          .map(e => e.href || e.src).filter(url => url.startsWith(location.origin) && !url.includes('#')))]""")
        assets += [urljoin(args.url, path) for path in ("assets/preview.png", "sitemap.xml", "robots.txt")]
        for asset in assets:
            response = context.request.get(asset)
            assert response.ok, (asset, response.status)
            if urlparse(asset).path.endswith(".pdf"):
                assert response.body().startswith(b"%PDF-"), asset
        assert page.locator('a[href$=".pdf"]').count() == 7
        assert page.locator(".project-card").count() == 4
        assert page.locator("h1").count() == 1
        assert not page.evaluate("() => [...document.querySelectorAll('a[href^=\"#\"]')].map(e => e.getAttribute('href').slice(1)).filter(id => !document.getElementById(id))")
        assert not page.evaluate("() => [...document.querySelectorAll('[id]')].map(e=>e.id).filter((id,i,ids)=>ids.indexOf(id)!==i)")
        expect(page.locator("#profile-photo")).to_be_hidden()
        expect(page.locator(".portrait-monogram")).to_be_visible()
        results["checks"].append(f"{len(assets)} local resources return HTTP 200; 7 valid PDF downloads; all anchor targets; avatar fallback")

        page.set_viewport_size({"width": 375, "height": 812})
        menu = page.locator(".menu-toggle")
        nav = page.locator("#main-nav")
        menu.focus()
        page.keyboard.press("Enter")
        expect(nav).to_be_visible()
        expect(menu).to_have_attribute("aria-expanded", "true")
        page.keyboard.press("Escape")
        expect(nav).to_be_hidden()
        expect(menu).to_be_focused()
        page.keyboard.press("Space")
        page.locator('#main-nav a[href="#projects"]').focus()
        page.keyboard.press("Enter")
        expect(nav).to_be_hidden()
        expect(page.locator("#projects")).to_be_focused()
        menu.focus()
        page.keyboard.press("Enter")
        page.set_viewport_size({"width": 1024, "height": 1000})
        expect(menu).to_have_attribute("aria-expanded", "false")
        expect(nav).to_be_visible()
        page.locator('.footer-links a[href="#privacy-notice"]').click()
        expect(page.locator("#privacy-notice details")).to_have_attribute("open", "")
        results["checks"].append("Menu Enter/Space, Escape focus return, destination focus, desktop resize reset, privacy disclosure")

        page.evaluate("localStorage.clear()")
        page.reload(wait_until="networkidle")
        page.keyboard.press("Tab")
        expect(page.locator(".skip-link")).to_be_focused()
        assert page.locator(".skip-link").bounding_box()["y"] >= 0
        page.keyboard.press("Enter")
        assert page.url.endswith("#main")
        page.emulate_media(color_scheme="dark")
        expect(page.locator(".theme-toggle")).to_have_attribute("aria-label", "Switch to light mode")
        page.locator(".theme-toggle").click()
        assert page.evaluate("localStorage.getItem('portfolio-theme')") == "light"
        page.reload(wait_until="networkidle")
        expect(page.locator("html")).to_have_attribute("data-theme", "light")
        results["checks"].append("Visible keyboard skip link; system theme changes; theme toggle and reload persistence")

        page.locator(".portrait-frame").hover(position={"x": 10, "y": 10})
        expect(page.locator(".portrait-frame")).to_have_class(re.compile(r".*is-hovered.*"))
        assert page.locator(".portrait-frame").evaluate("e => e.style.getPropertyValue('--tilt-x')")
        page.mouse.move(0, 0)
        expect(page.locator(".portrait-frame")).not_to_have_class(re.compile(r".*is-hovered.*"))
        results["checks"].append("Fine-pointer glass highlight and portrait tilt activate on hover and reset on leave")

        page.emulate_media(reduced_motion="reduce")
        page.locator(".portrait-frame").hover(position={"x": 10, "y": 10})
        page.wait_for_timeout(100)
        assert page.evaluate("getComputedStyle(document.documentElement).scrollBehavior") == "auto"
        assert page.locator(".portrait-frame").evaluate("e => getComputedStyle(e).transform") == "none"
        assert page.locator(".button-primary").first.evaluate("e => getComputedStyle(e).transitionDuration") == "0s"
        assert page.locator(".project-card").first.evaluate("e => getComputedStyle(e).animationName") == "none"
        expect(page.locator(".portrait-frame")).not_to_have_class(re.compile(r".*is-hovered.*"))
        cdp = context.new_cdp_session(page)
        cdp.send("Emulation.setEmulatedMedia", {"features": [{"name": "prefers-reduced-transparency", "value": "reduce"}]})
        assert page.locator(".site-header").evaluate("e => getComputedStyle(e).backdropFilter") == "none"
        assert page.locator(".portrait-frame").evaluate("e => getComputedStyle(e, '::after').display") == "none"
        results["checks"].append("Reduced motion disables smooth scroll, tilt, transitions and reveal; reduced transparency removes glass blur/reflection")

        nojs = browser.new_context(java_script_enabled=False, color_scheme="dark", viewport={"width": 320, "height": 812})
        nojs.route("https://avatars.githubusercontent.com/**", lambda route: route.abort())
        fallback = nojs.new_page()
        fallback.goto(args.url, wait_until="networkidle")
        for selector in ("#main-nav", "#projects", "#research", "#certifications", "#about", "#contact", "noscript .form-availability"):
            expect(fallback.locator(selector)).to_be_visible()
        expect(fallback.locator(".theme-toggle")).to_be_hidden()
        expect(fallback.locator(".menu-toggle")).to_be_hidden()
        assert fallback.locator(".inquiry-step:visible").count() == 4
        assert fallback.evaluate("document.documentElement.scrollWidth <= innerWidth")
        assert fallback.evaluate("getComputedStyle(document.body).backgroundColor") == "rgb(17, 22, 32)"
        fallback.screenshot(path=str(args.screenshots / "portfolio-nojs-320.png"), full_page=True)
        nojs.close()
        results["checks"].append("320px no-JavaScript dark mode: navigation, all content/form sections, email fallback visible; no overflow")

        error_response = context.request.get(urljoin(args.url, "404.html"))
        assert error_response.ok
        missing = urljoin(args.url, "missing/nested/page")
        assert context.request.get(missing).status == 404
        # Python's server has no Pages fallback, so model GitHub Pages' custom 404 routing.
        page.route(missing, lambda route: route.fulfill(status=404, content_type="text/html", body=error_response.body()))
        assert page.goto(missing, wait_until="networkidle").status == 404
        expect(page.locator("h1")).to_have_text("This page isn’t here.")
        assert page.locator('link[rel="stylesheet"]').evaluate("e => !!e.sheet")
        assert page.locator(".button-primary").get_attribute("href") == urlparse(args.url).path
        page.locator(".button-primary").click()
        expect(page.locator("#hero-title")).to_be_visible()
        results["checks"].append("Local missing path returns 404; simulated Pages nested custom 404 loads stylesheet and home link")
        assert not errors, errors
        results["checks"].append("No uncaught browser JavaScript errors")
        results["browser"] = browser.version
        browser.close()
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    run()
