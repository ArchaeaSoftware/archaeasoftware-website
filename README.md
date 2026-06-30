# archaeasoftware.com

A static mirror of [archaeasoftware.com](https://archaeasoftware.com), ready to deploy on
**Cloudflare Pages**. The original site is WordPress (Twenty Twenty-Four theme); this is a
faithful, byte-for-byte capture of the rendered pages with all WordPress backend machinery
(PHP, REST API, feeds, emoji loader, XML-RPC) removed. It is pure HTML/CSS/JS/fonts/images
and needs no server runtime.

## Structure

```
index.html              Homepage
about/index.html        About page
wp-content/             Theme assets (CSS, fonts) and uploaded images
wp-includes/            WordPress core block stylesheets + nav interactivity JS modules
_headers                Cloudflare Pages: security + caching headers
_redirects              Cloudflare Pages: retire old WordPress URLs
```

All asset references are root-relative (`/wp-content/...`), so the site is host-agnostic and
works unchanged on a Pages preview URL or the production domain.

## Local preview

```sh
python3 -m http.server 8000
# open http://localhost:8000
```

## Deploy to Cloudflare Pages

### Option A — Git integration (recommended)

1. Push this repo to GitHub (see below).
2. In the Cloudflare dashboard: **Workers & Pages → Create → Pages → Connect to Git**.
3. Select this repository.
4. Build settings:
   - **Framework preset:** None
   - **Build command:** *(leave empty)*
   - **Build output directory:** `/`
5. Deploy. Every push to the main branch auto-publishes.
6. Add the custom domain under **Custom domains** (`archaeasoftware.com`). Cloudflare will
   manage DNS if the zone is on your account.

### Option B — Direct upload with Wrangler

```sh
npm install -g wrangler          # or use: npx wrangler
wrangler login
wrangler pages deploy . --project-name archaeasoftware
```

## Re-syncing from the live WordPress site

The static capture was produced by `scripts/mirror.py`. Re-run it to refresh content after
editing the live site:

```sh
python3 scripts/mirror.py .
```

It downloads the homepage and About page, strips WordPress backend tags, localizes all
assets to clean paths, and rewrites URLs to root-relative.
