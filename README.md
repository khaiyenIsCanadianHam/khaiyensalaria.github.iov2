# Khaiyen Salaria — portfolio

A static portfolio for **Khaiyen Alexander R. Salaria**, a freelance web developer and Computer Science student in Manila, Philippines. It presents four projects, supplied academic documents and certificates, and a structured project inquiry form. The website uses HTML, CSS, and vanilla JavaScript; no build step or application server is required.

The intended GitHub Pages address is **https://khaiyeniscanadianham.github.io/khaiyensalaria.github.iov2/**. A Git push alone does not establish that GitHub Pages is enabled or that the website is live.

## Run locally

From this repository:

```bash
python3 -m http.server 8000 --bind 127.0.0.1 --directory ..
```

Open `http://localhost:8000/khaiyensalaria.github.iov2/`. Serving the parent directory reproduces the project-site path used by the custom 404 page. Stop the server with `Ctrl+C`. No dependency installation is needed. Use the existing checkout in a Codex cloud task; the task already has an isolated environment, so do not create a Git worktree unless explicitly requested.

## Design rationale

The supplied `04_Design` documents describe Euraolly's design system. This portfolio adapts their interaction and visual principles to Khaiyen's personal identity; it does not claim an affiliation with that platform.

1. **Clarity first:** descriptive headings, concise copy, and an obvious inquiry action keep the work and contact path easy to understand.
2. **Consistent visual language:** reusable CSS properties govern colors, spacing, typography, surfaces, and interaction states.
3. **Readable hierarchy:** responsive type and restrained line lengths organize the hero, projects, research, credentials, and form.
4. **Purposeful depth:** borders, subtle shadows, and restrained glass surfaces give the interface depth while keeping text readable in both themes.
5. **Useful feedback:** pointer-responsive liquid-glass highlights, gentle section reveals, hover, focus, validation, and submission states communicate what visitors can do and what happened.
6. **Inclusive interaction:** native scrolling, keyboard controls, reduced motion, and responsive layouts support different devices and preferences.
7. **Honest presentation:** verified repository descriptions, original PDFs, and clearly identified demonstration imagery support the portfolio without invented results or testimonials.

The source documents also discuss cinematic scrolling, magnetic cursors, 3D scenes, and live mockups. These can obstruct keyboard interaction, cause motion discomfort, or add unnecessary rendering cost here. Native scrolling and pointers, lightweight CSS depth, visible focus states, and a real repository screenshot provide accessible alternatives. Liquid-glass reflections track fine pointers, the portrait tilts by at most two degrees, and sections reveal once as they enter view. Reduced motion disables these movements; reduced transparency removes reflections. No content depends on the effects. Content must remain available without animation, backdrop blur, or JavaScript. Reduced-motion preferences take priority over decorative transitions.

## Files and content

- `index.html`: page content, navigation, metadata, inquiry form, and privacy notice.
- `style.css`: responsive layouts, reusable design tokens, light/dark themes, and reduced-motion behavior.
- `theme.js` and `script.js`: initial theme, theme toggle, navigation, and progressive interface behavior.
- `form.js`: inquiry steps, validation, conditional questions, review, and submission.
- `404.html`: matching error page with a link back to the project-site homepage.
- `assets/documents/`: the seven original supplied PDF documents.
- `assets/images/`: local imagery, including the Hanami dashboard screenshot with fictional demonstration data.
- `robots.txt`, `sitemap.xml`, and `favicon.svg`: search and browser assets.
- [`docs/content-sources.md`](docs/content-sources.md): source references, verified facts, and content limitations.

## Enable inquiry delivery with Web3Forms

The form endpoint is `https://api.web3forms.com/submit`. Its `access_key` is intentionally empty until the owner supplies a real public form key. Live submission and email delivery cannot be verified without that key. Direct email to **khaiyenbusiness@gmail.com** remains the alternative contact method.

1. Visit [Web3Forms](https://web3forms.com/) and create a form access key for `khaiyenbusiness@gmail.com`. Complete any email verification requested by the provider.
2. In `index.html`, find the hidden input named `access_key` and put the issued key in its `value` attribute. This is a public form access key designed for frontend use. Never put an SMTP password, private API credential, or mailbox password in this repository.
3. Keep the native `POST` action, `subject`, `from_name`, and honeypot fields intact. The `email` field supplies the visitor's reply address. JavaScript enhances submission without removing the native form action.
4. Publish the updated files and submit one clearly labeled test inquiry using an address you control. Confirm both the page result and receipt in the destination mailbox, including its spam folder.
5. Check the received notification for the contact details, selected project type, selected features, relevant conditional answer, budget, timeline, description, and privacy acknowledgment. Optional empty fields must not prevent submission.
6. Test a failed response or blocked connection locally. The form must retain entered values, show a useful error, and allow a retry. Do not repeatedly send live tests or send real client information during testing.
7. Review Web3Forms' current free-plan spam protection and domain settings. Keep the honeypot; enable additional controls only when supported by the chosen plan and the implementation.

If delivery fails, check the key, verified destination email, provider response, spam folder, browser console/network panel, and provider limits. Success requires a successful HTTP response and the API's success indicator; a sent request alone is insufficient. Browser-level tests with simulated API responses do not establish real email delivery.

To change the destination inbox, configure or create the appropriate key through Web3Forms, replace the public key if needed, and repeat the delivery test. Editing the displayed email address alone does not change where Web3Forms sends messages.

## Publish on GitHub Pages

This repository is a **project site**. Keep its current name unless intentionally migrating the website.

1. Commit and push the static files to `main` in `khaiyenIsCanadianHam/khaiyensalaria.github.iov2`.
2. In GitHub, open **Settings → Pages**. Under **Build and deployment**, choose **Deploy from a branch**, select **main**, choose **/ (root)**, and save.
3. Wait for GitHub's Pages deployment to complete. Open the URL shown in the Pages settings. For the current name, the expected address is `https://khaiyeniscanadianham.github.io/khaiyensalaria.github.iov2/`.
4. Check the homepage, CSS/JavaScript, PDF downloads, theme controls, and an intentionally missing path. Confirm the custom 404 link returns to the project homepage.
5. Test inquiry delivery after the real Web3Forms key is configured. Check the public page on a phone as well as a desktop browser.

For a user site at `https://khaiyeniscanadianham.github.io/`, use a repository named `khaiyeniscanadianham.github.io` instead. A custom domain is optional: configure it in Pages, follow GitHub's current DNS instructions, and enable HTTPS when available. Before a URL change, update canonical, Open Graph, structured-data, sitemap, robots sitemap reference, and 404-home URLs together. Relative asset paths allow the current project subdirectory to work.

## Maintain the portfolio

| Change | Where and how |
| --- | --- |
| Add a project | Copy a project entry in `index.html`; provide a verified description, useful technology tags, repository URL, and a real demo link only when available. Add its source and any limitations to `docs/content-sources.md`. |
| Update biography or contact details | Edit the About/Contact content in `index.html`; keep the hero, footer, metadata, and structured data consistent. Only list confirmed roles and experience. |
| Add research | Put the original PDF in `assets/documents/`; add an entry and source note. Identify concept papers and academic work accurately. Confirm the year and contribution before claiming either. |
| Add a certificate | Add its PDF and a concise entry with the exact course name, issuer, and issue date. Use an official verification URL only if supplied or confirmed. |
| Change inquiry options or budget ranges | Edit the relevant options in `index.html`. If changing project-type values or conditional questions, update the corresponding logic in `form.js` and retest switching categories. Budget ranges qualify inquiries; they are not price packages. |
| Change the delivery inbox | Update the form configuration through Web3Forms and replace its public key when needed; test actual receipt. Also update visible email links and privacy contact details when applicable. |
| Replace imagery | Add an optimized local file under `assets/images/`, then update its `src`, meaningful `alt`, and intrinsic dimensions. Keep the demonstration-data caption on any screenshot that contains sample records. |
| Update SEO | Edit the title, description, canonical, Open Graph/Twitter fields, and structured data in `index.html`; keep `sitemap.xml`, `robots.txt`, and 404 links consistent with the final URL. |
| Change appearance | Edit the theme tokens and reusable rules in `style.css`, then check contrast, focus, small screens, and both themes. |

Recommended assets: a square local portrait of roughly 600–1000 pixels per side; consistent landscape project images around 1200 × 750 pixels; and an Open Graph preview of 1200 × 630 pixels. Use WebP or AVIF for photos where practical. Do not substitute fabricated product screenshots or portraits. Keep original PDFs unchanged unless the owner supplies revised versions.

## Configuration and content still to confirm

- **Required for inquiry delivery:** real Web3Forms public access key in `index.html`, followed by a confirmed mailbox delivery test.
- **Portrait:** the inline supplied photo has no locally accessible file in this task. The temporary image uses the owner's GitHub avatar URL with an initials fallback. Upload the exact photo as a local JPG/PNG, optimize it as `assets/images/profile.webp`, and update the image source and dimensions to remove the external dependency.
- **Research details:** confirm years and individual contributions for the rural education, digital literacy, and data analyst concept documents. The Python permutations/combinations paper explicitly names Khaiyen as a co-author and is dated 2025.
- **Digital literacy PDF:** its cover repeats the rural education title. Confirm or replace the document before asserting a corrected formal title; its current label follows the supplied filename and body topic.
- **Optional:** confirmed live project demos, additional authentic project screenshots, employment/client experience, and additional custom preview imagery. These are not invented or required for the existing layout. A 1200 × 630 brand preview is included at `assets/preview.png`.
- **Optional Search Console:** `[GOOGLE_SEARCH_CONSOLE_VERIFICATION_CODE]`. Add the verification meta tag only after receiving an actual code; never publish this placeholder as a verification value.
- **Hosting:** confirm Pages is enabled and its deployment succeeds. The configured production URL follows the repository name; no custom domain was provided.

## Release and regression checklist

These are checks to perform, not claims that every item has already passed. Record executed checks and their results in the task's delivery report.

- [ ] Load the page at 320, 375, 768, 1024, 1440, and 1920 CSS pixels; inspect landscape orientation, 200% zoom, long text, sticky navigation, and horizontal overflow.
- [ ] Use only the keyboard to navigate the skip link, menu, theme control, links, and all form steps. Confirm visible focus, sensible order, and no keyboard traps.
- [ ] Review headings, labels, progress announcements, error associations, focus changes, and submission feedback with a screen reader.
- [ ] Check text/control contrast, focus indicators, and touch targets in light and dark themes. Check system preference and saved explicit theme selection.
- [ ] Enable reduced motion and verify that content remains visible and interaction remains usable. Check basic content and contact options with JavaScript disabled.
- [ ] Follow internal navigation, social/repository links, all seven PDF links, and available real demo links. Verify no optional missing image breaks layout.
- [ ] Test required fields, invalid email/URL values, length limits, optional unanswered fields, and privacy acknowledgment.
- [ ] Move forward/backward through the form; retain values; verify review text; verify focus on an invalid field and a newly opened step.
- [ ] Change project types after entering conditional answers. Confirm irrelevant answers are not submitted and features appear once as a readable list.
- [ ] Test success, provider rejection, invalid response, connection failure, timeout, and duplicate-click behavior using simulated responses before a live test. Clear entered data only after confirmed success.
- [ ] With the real key configured, verify native form submission, JavaScript submission, reply-to address, actual notification delivery, and supported spam protection.
- [ ] Review the privacy notice, public contact address, provider disclosure, and absence of inquiry details in local storage or analytics.
- [ ] Inspect page title, description, canonical, Open Graph metadata, structured data, sitemap URLs, and robots rules at the deployed address.
- [ ] Run Lighthouse on mobile and desktop. Scores of 90+ are targets; record actual measurements and conditions. Use Google's Rich Results Test where the structured-data type is supported; valid Person data does not guarantee a rich result.
- [ ] Confirm the deployed custom 404 page, project-subdirectory asset paths, and HTTPS behavior.

## Automated browser checks

The production site has no dependencies. Optional developer checks use Python Playwright and an installed Chromium browser. With the local server running, run:

```bash
python3 tests/form_smoke.py --base-url http://127.0.0.1:8000/khaiyensalaria.github.iov2/
python3 tests/site_smoke.py --base-url http://127.0.0.1:8000/khaiyensalaria.github.iov2/
```

The form suite intercepts Web3Forms requests and never sends live inquiries. See `docs/validation.md` for executed outcomes and remaining manual checks.
