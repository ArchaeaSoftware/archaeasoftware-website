# archaeasoftware.com

A static mirror of [archaeasoftware.com](https://archaeasoftware.com), deployed on
**Cloudflare** as a static-assets Worker. The original site is WordPress (Twenty
Twenty-Four theme); this is a faithful capture of the rendered pages with all WordPress
backend machinery (PHP, REST API, feeds, emoji loader, XML-RPC) removed. It is pure
HTML/CSS/JS/fonts/images and needs no server runtime.

## Structure

```
public/                 Everything served to the web (the assets directory)
  index.html            Homepage
  about/index.html      About page
  wp-content/           Theme assets (CSS, fonts) and uploaded images
  wp-includes/          WordPress core block stylesheets + nav interactivity JS
  _headers              Cloudflare: security + caching headers
  _redirects            Cloudflare: retire old WordPress URLs
wrangler.jsonc          Cloudflare Worker config (serves ./public as static assets)
scripts/mirror.py       Re-sync tool: re-captures the live WordPress site
```

Only `public/` is published — repo metadata, config, and scripts live outside it and are
never served. All asset references are root-relative (`/wp-content/...`), so the site is
host-agnostic and works unchanged on a `*.workers.dev` URL or the production domain.

## Local preview

```sh
cd public && python3 -m http.server 8000
# open http://localhost:8000
```

## Deploy to Cloudflare

Deployment is a static-assets Worker defined by [`wrangler.jsonc`](wrangler.jsonc)
(`assets.directory` = `./public`, no Worker script).

### Connected build (recommended)

The repo is connected to Cloudflare Workers Builds. On every push to `main`, Cloudflare runs:

- **Build command:** *(none)*
- **Deploy command:** `npx wrangler deploy`

and publishes `public/`. Add `archaeasoftware.com` under the Worker's
**Settings → Domains & Routes → Custom domain**.

### Manual deploy

```sh
npx wrangler login
npx wrangler deploy
```

## Re-syncing from the live WordPress site

The static capture was produced by [`scripts/mirror.py`](scripts/mirror.py). Re-run it to
refresh content after editing the live site (it writes into the assets directory):

```sh
python3 scripts/mirror.py public
```

It downloads the homepage and About page, strips WordPress backend tags, localizes all
assets to clean query-string-free paths, and rewrites URLs to root-relative.
