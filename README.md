# alex-blythe.com

Static Astro source for Alex Blythe's aerospace engineering and research website.

## Local development

```powershell
.\site.cmd install
.\site.cmd dev
```

## Production build

```powershell
.\site.cmd build
.\site.cmd preview
```

Pushes to `main` deploy through GitHub Actions. The `CNAME` file publishes the site for `alex-blythe.com` once the domain's DNS records point to GitHub Pages.
