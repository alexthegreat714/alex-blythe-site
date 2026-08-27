# WordPress to GitHub Pages handoff

## Prepared

- Standalone Astro site with the approved homepage
- Existing headshot and Bifrost Drive PDF stored locally
- The three published WordPress article URLs reproduced as static pages
- `CNAME`, `robots.txt`, sitemap, canonical metadata, and GitHub Pages workflow
- Full WordPress content export and media archive retained outside this repository under `website/migration`

## Complete after GitHub sign-in

1. Create a public GitHub repository and push this folder to its `main` branch.
2. In **Settings → Pages**, select **GitHub Actions** as the source.
3. Confirm the first deployment succeeds at the temporary `github.io` URL.
4. Add `alex-blythe.com` as the custom domain and confirm the GitHub account name used for the `www` CNAME.
5. At the WordPress registrar, keep the domain registration and replace only the website DNS records with GitHub Pages records.
6. Verify the apex domain, `www`, HTTPS, homepage, PDF, articles, contact link, desktop layout, and mobile layout.
7. Only after those checks pass, cancel the **WordPress.com Personal Plan**. Do not cancel **Domain Registration: alex-blythe.com**.

## GitHub Pages apex records

```text
A 185.199.108.153
A 185.199.109.153
A 185.199.110.153
A 185.199.111.153
```

Set `www` to a CNAME for `<github-account>.github.io` after the destination account is confirmed.
