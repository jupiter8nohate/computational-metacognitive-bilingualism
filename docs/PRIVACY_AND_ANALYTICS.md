# Privacy and analytics

CMB treats measurement as an observability function, not as authority over a person.

```text
MEASUREMENT != IDENTITY
TRAFFIC != PERSON
PROFILE != HUMAN
ANALYTICS != CONSENT
```

## Current status

Client-side analytics are **disabled by default**.

The public documentation loads a small provider-neutral analytics adapter, but the adapter sends no analytics request while `enabled` is `false` in `docs/javascripts/cmb-analytics-config.js`.

The adapter also refuses to initialize a provider when the browser exposes Global Privacy Control or Do Not Track.

## Supported activation paths

The adapter currently supports two explicit providers:

- `ga4` for Google Analytics 4
- `plausible` for Plausible Analytics

Activation requires a reviewed repository change that supplies a real provider identifier. Fake IDs and placeholder tracking are intentionally rejected.

For GA4, the adapter strips query strings and fragments from the transmitted page location and disables Google signals and ad-personalization signals in the local configuration call.

For Plausible, the adapter requires an explicit site domain and script endpoint.

## Search Console is separate

Google Search Console is not implemented through this browser adapter. Search Console measures search visibility and indexing through Google's webmaster systems rather than through the CMB page JavaScript.

CMB may use Search Console, URL inspection, sitemap reporting, IndexNow, or other search-observability systems independently from client-side analytics.

## Data minimization rule

Any future analytics activation should collect the minimum information necessary to answer operational questions such as:

- Which public pages receive visits?
- Which pages are discovered through search?
- Which documentation routes are useful enough to keep improving?
- Are deployments causing visibility or navigation regressions?

CMB analytics should not be used to infer a visitor's identity, inner state, ideology, diagnosis, destiny, or moral worth.

```text
OBSERVE THE SYSTEM.
DO NOT CLAIM OWNERSHIP OF THE PERSON.

HUMAN_AGENCY > MACHINE_AUTHORITY
```

## Runtime inspection

Developers can inspect the adapter locally in the browser console:

```javascript
window.CMBAnalytics.status()
```

With the default configuration, the expected result reports analytics as disabled and no external analytics provider is loaded.
