(() => {
  "use strict";

  const config = window.CMB_ANALYTICS_CONFIG || {};
  const privacySignal =
    navigator.globalPrivacyControl === true ||
    navigator.doNotTrack === "1" ||
    window.doNotTrack === "1";

  const state = {
    enabled: false,
    provider: null,
    reason: "disabled",
  };

  function expose() {
    window.CMBAnalytics = Object.freeze({
      status: () => ({ ...state }),
    });
  }

  if (!config.enabled) {
    expose();
    return;
  }

  if (privacySignal) {
    state.reason = "privacy-signal";
    expose();
    return;
  }

  function loadGa4(measurementId) {
    if (!/^G-[A-Z0-9]+$/i.test(measurementId || "")) {
      throw new Error("Invalid GA4 measurement ID");
    }

    window.dataLayer = window.dataLayer || [];
    window.gtag = function gtag() {
      window.dataLayer.push(arguments);
    };

    const script = document.createElement("script");
    script.async = true;
    script.referrerPolicy = "strict-origin-when-cross-origin";
    script.src = `https://www.googletagmanager.com/gtag/js?id=${encodeURIComponent(measurementId)}`;
    document.head.appendChild(script);

    window.gtag("js", new Date());
    window.gtag("config", measurementId, {
      allow_ad_personalization_signals: false,
      allow_google_signals: false,
      page_location: `${window.location.origin}${window.location.pathname}`,
      page_title: document.title,
    });
  }

  function loadPlausible(domain, scriptSrc) {
    if (!domain || !/^[a-z0-9.-]+$/i.test(domain)) {
      throw new Error("Invalid Plausible domain");
    }

    const script = document.createElement("script");
    script.defer = true;
    script.dataset.domain = domain;
    script.referrerPolicy = "strict-origin-when-cross-origin";
    script.src = scriptSrc || "https://plausible.io/js/script.js";
    document.head.appendChild(script);
  }

  try {
    if (config.provider === "ga4") {
      loadGa4(config.ga4MeasurementId);
      state.enabled = true;
      state.provider = "ga4";
      state.reason = "active";
    } else if (config.provider === "plausible") {
      loadPlausible(config.plausibleDomain, config.plausibleScriptSrc);
      state.enabled = true;
      state.provider = "plausible";
      state.reason = "active";
    } else {
      state.reason = "unsupported-provider";
    }
  } catch (error) {
    state.reason = "configuration-error";
    console.warn("CMB analytics not started:", error.message);
  }

  expose();
})();
