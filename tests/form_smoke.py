"""Exercise the inquiry in a real browser without sending any email.

Run a static server at the repository root, then:
    python tests/form_smoke.py --base-url http://127.0.0.1:8000/

Requires the optional Python Playwright testing package and a Chromium browser.
The website itself has no package or build dependencies.
"""

import argparse
import json
import os
import re

from playwright.sync_api import expect, sync_playwright


API = "https://api.web3forms.com/submit"


def run(base_url: str, browser_path: str) -> None:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            executable_path=browser_path, headless=True, args=["--no-sandbox"]
        )
        context = browser.new_context(viewport={"width": 390, "height": 844})
        # Safety net: only page-level mocked responses can reach this endpoint.
        context.route("https://api.web3forms.com/**", lambda route: route.abort())
        page = context.new_page()
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto(base_url)
        form = page.locator("#inquiry-form")
        expect(form).to_have_class(re.compile(r"\bis-enhanced\b"))
        next_button = form.locator("[data-form-next]")
        previous_button = form.locator("[data-form-previous]")
        submit_button = form.locator("[data-form-submit]")
        feedback = form.locator("[data-form-feedback]")
        name = form.locator('[name="name"]')
        email = form.locator('[name="email"]')
        website = form.locator('[name="existing_website"]')
        message = form.locator('[name="message"]')

        expect(form.locator('[data-step="0"]')).to_be_visible()
        expect(form.locator('[data-step="1"]')).to_be_hidden()
        expect(form.locator("[data-form-availability]")).to_be_visible()
        next_button.click()
        expect(name).to_be_focused()
        expect(name).to_have_attribute("aria-invalid", "true")
        expect(form.locator("#inquiry-name-error")).to_be_visible()
        name.fill("Alex Example")
        email.fill("not-an-email")
        next_button.click()
        expect(email).to_be_focused()
        email.fill("alex@example.invalid")
        website.fill("example.invalid")
        next_button.click()
        expect(website).to_be_focused()
        website.fill("https://example.invalid")
        # Pressing Enter advances the wizard without sending a request.
        website.press("Enter")
        expect(form.locator('[data-step="1"]')).to_be_visible()
        expect(form.locator('[data-step="1"] > legend')).to_be_focused()
        next_button.click()
        expect(form.locator('[name="project_type"]')).to_be_focused()

        form.locator('[name="project_type"]').select_option("E-commerce / Online Store")
        products = form.locator('[name="approximate_product_count"]')
        products.fill("12.5")
        form.locator('[name="online_checkout"]').select_option("Yes")
        next_button.click()
        expect(products).to_be_focused()
        expect(products).to_have_attribute("aria-invalid", "true")
        products.fill("12")
        next_button.click()
        expect(form.locator('[data-step="2"]')).to_be_visible()
        previous_button.click()
        expect(products).to_have_value("12")

        # Switching categories must keep old answers out of the actual payload.
        form.locator('[name="project_type"]').select_option("Custom Web Application")
        expect(products).to_be_disabled()
        expect(products).to_be_hidden()
        application = form.locator('[name="application_requirements"]')
        application.fill("Members should be able to manage appointments.")
        form.locator('[name="requested_features"][value="Contact Form"]').check()
        form.locator('[name="requested_features"][value="Online Payments"]').check()
        next_button.click()
        next_button.click()
        expect(message).to_be_focused()
        expect(message).to_have_attribute("aria-invalid", "true")
        inquiry = 'Build a scheduling tool. <img src=x onerror="alert(1)">'
        message.fill(inquiry)
        form.locator('[name="estimated_budget"]').select_option("₱5,000–₱10,000")
        # The unanswered optional timeline and goal must not block review.
        next_button.click()
        review = form.locator("[data-review-summary]")
        expect(review).to_contain_text(inquiry)
        expect(review.locator("img, script")).to_have_count(0)
        expect(review).to_contain_text("Not specified")
        expect(review).not_to_contain_text("Approximate product count")
        submit_button.click()
        consent = form.locator('[name="privacy_acknowledgment"]')
        expect(consent).to_be_focused()
        consent.check()
        submit_button.click()
        expect(feedback).to_contain_text("Online submission is not available yet")
        expect(feedback.locator('a[href="mailto:khaiyenbusiness@gmail.com"]')).to_be_visible()
        expect(message).to_have_value(inquiry)
        print("PASS: validation, keyboard navigation, conditions, review escaping, missing-key fallback")

        # A test-only value is injected into this browser; the source remains empty.
        form.locator('[name="access_key"]').evaluate("element => { element.value = 'test-only-public-key'; }")
        sent_payloads = []
        mock = {"status": 422, "body": json.dumps({"success": False})}

        def answer_request(route):
            sent_payloads.append(route.request.post_data_json)
            route.fulfill(
                status=mock["status"],
                body=mock["body"],
                headers={"content-type": "application/json", "access-control-allow-origin": "*"},
            )

        page.route(API, answer_request)
        submit_button.click()
        expect(feedback).to_contain_text("I could not confirm")
        expect(submit_button).to_be_enabled()
        expect(message).to_have_value(inquiry)
        assert len(sent_payloads) == 1
        payload = sent_payloads[0]
        assert payload["requested_features"] == "Contact Form, Online Payments"
        assert isinstance(payload["requested_features"], str)
        assert "approximate_product_count" not in payload
        assert "online_checkout" not in payload
        assert "booking_requirements" not in payload
        assert payload["application_requirements"] == application.input_value()
        assert payload["message"] == inquiry
        assert payload["email"] == "alex@example.invalid"
        assert payload["privacy_acknowledgment"] == "Acknowledged"

        for status, body in [
            (200, "not valid JSON"),
            (500, json.dumps({"success": True})),
            (200, json.dumps({"success": "true"})),
        ]:
            mock.update(status=status, body=body)
            submit_button.click()
            expect(feedback).to_contain_text("I could not confirm")
            expect(submit_button).to_be_enabled()
            expect(message).to_have_value(inquiry)
        print("PASS: single feature field, stale-answer exclusion, HTTP/JSON/API failure handling and retained draft")

        # Hold a mocked request open to check duplicate protection and busy controls.
        page.evaluate("""() => {
            window.originalFetch = window.fetch;
            window.mockCallCount = 0;
            window.fetch = () => {
                window.mockCallCount += 1;
                return new Promise(resolve => { window.completeMockRequest = resolve; });
            };
            const form = document.getElementById('inquiry-form');
            form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
            form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
        }""")
        assert page.evaluate("window.mockCallCount") == 1
        expect(form).to_have_attribute("aria-busy", "true")
        expect(submit_button).to_be_disabled()
        expect(previous_button).to_be_disabled()
        expect(message).to_be_disabled()
        page.evaluate("window.completeMockRequest({ok: false, json: async () => ({success: false})})")
        expect(submit_button).to_be_enabled()
        expect(message).to_have_value(inquiry)

        # Use the actual timeout/AbortController path with a short test-only delay.
        page.evaluate("""() => {
            window.originalSetTimeout = window.setTimeout;
            window.setTimeout = (callback, delay, ...args) => window.originalSetTimeout(callback, delay === 20000 ? 25 : delay, ...args);
            window.fetch = (_url, options) => new Promise((_resolve, reject) => {
                options.signal.addEventListener('abort', () => reject(new DOMException('Aborted', 'AbortError')));
            });
        }""")
        submit_button.click()
        expect(feedback).to_contain_text("request timed out")
        expect(feedback).to_contain_text("may have reached me")
        expect(message).to_have_value(inquiry)
        expect(submit_button).to_be_enabled()
        page.evaluate("window.fetch = window.originalFetch; window.setTimeout = window.originalSetTimeout;")
        print("PASS: duplicate request guard, busy state, timeout recovery")

        mock.update(status=200, body=json.dumps({"success": True}))
        submit_button.click()
        expect(feedback).to_contain_text("submitted successfully")
        expect(feedback).to_be_focused()
        expect(form).to_have_attribute("aria-busy", "false")
        expect(form.locator('[data-step="0"]')).to_be_visible()
        expect(name).to_have_value("")
        expect(email).to_have_value("")
        expect(message).to_have_value("")
        expect(consent).not_to_be_checked()
        expect(form.locator('[name="requested_features"]:checked')).to_have_count(0)
        assert errors == [], errors
        print("PASS: explicit API success resets form and focuses confirmation; no JavaScript errors")

        fallback = browser.new_context(java_script_enabled=False)
        fallback.route("https://api.web3forms.com/**", lambda route: route.abort())
        fallback_page = fallback.new_page()
        fallback_page.goto(base_url)
        native_form = fallback_page.locator("#inquiry-form")
        for index in range(4):
            expect(native_form.locator(f'[data-step="{index}"]')).to_be_visible()
        expect(native_form).to_have_attribute("action", API)
        expect(native_form).to_have_attribute("method", "POST")
        assert native_form.get_attribute("novalidate") is None
        expect(native_form.locator('[data-form-submit]')).to_be_visible()
        expect(native_form.locator('[data-form-next]')).to_be_hidden()
        assert "access key" in native_form.locator("noscript").inner_html()
        print("PASS: native no-JavaScript fallback exposes fields and retains native POST/validation")
        fallback.close()
        context.close()
        browser.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8000/")
    parser.add_argument("--browser", default=os.environ.get("CHROMIUM_PATH", "/usr/bin/chromium"))
    arguments = parser.parse_args()
    run(arguments.base_url, arguments.browser)
