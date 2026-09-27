# Activate the two legacy HTTP redirects

Current hosting: GitHub Pages origin; Cloudflare authoritative DNS. The apex currently resolves directly to GitHub Pages IPs, so Cloudflare redirect rules do not intercept its requests. GitHub Pages serves the existing moved-page HTML with HTTP 200. Neither Astro meta refresh nor a `_redirects` file changes that host's response status.

`legacy-redirect-rules.json` defines **Cloudflare Single Redirects**, not HTML or JavaScript redirects. It covers only the two retired page families on the apex and `www`, including their slash, non-slash, and `index.html` forms. Each goes straight to its final HTTPS canonical URL, preserving query parameters. No other path, private subdomain, book or paper is matched.

## Account-required activation

1. Sign in to the existing Cloudflare account for `alex-blythe.com`.
2. Inspect existing rules and TLS configuration. Add the two rules under Rules → Redirect Rules using the expressions and static destinations in the JSON. Set **301** and **Preserve query string**. Keep any unrelated rules; do not replace an existing phase ruleset with this two-rule document.
3. For the apex and `www` only, enable proxying on their existing website DNS records, preserving the GitHub Pages origin targets. Check that TLS to the origin remains verified and that existing rules do not introduce a preceding redirect. Do not change nameservers, private subdomains, mail records or tunnel configuration.
4. Run `npm run audit:redirects` after activation. It makes real HEAD requests, checks the exact Location, then requests that Location without following further redirects. Both old URLs must return 301/308 and both destinations must return 200 in one hop. Query/slash/`index.html` variants are checked too.
5. Verify ordinary pages, the Bifrost PDF and Road to Type 2 remain available. An unknown path must still be 404. Do not declare this complete solely because the rules were saved.

The current HTML fallback files are unchanged, not the proposed fix. They remain a deployment blocker until intercepted by the real edge redirect. There is deliberately no local/mock success substituted for the public header audit.

References: [Cloudflare Single Redirects settings](https://developers.cloudflare.com/rules/url-forwarding/single-redirects/settings/), [API rule format](https://developers.cloudflare.com/rules/url-forwarding/single-redirects/create-api/), [proxied DNS requirement](https://developers.cloudflare.com/rules/url-forwarding/).
