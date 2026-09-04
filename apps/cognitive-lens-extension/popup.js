const scanButton = document.querySelector("#scan");
const resultSection = document.querySelector("#result");
const levelNode = document.querySelector("#level");
const scoreNode = document.querySelector("#score");
const signalsNode = document.querySelector("#signals");

function analyzePage() {
  const observations = [];

  const autoplayVideos = [...document.querySelectorAll("video[autoplay]")].filter(
    (video) => !video.paused || video.autoplay,
  );
  if (autoplayVideos.length > 0) {
    observations.push({
      kind: "autoplay_media",
      weight: Math.min(25, 10 + autoplayVideos.length * 5),
      evidence: `${autoplayVideos.length} autoplay video element(s) observed.`,
    });
  }

  const interactive = [...document.querySelectorAll("button, a, [role='button']")];
  const engagementPattern = /like|share|follow|subscribe|comment|react|engage/i;
  const engagementMatches = interactive.filter((node) =>
    engagementPattern.test((node.textContent || "").trim()),
  );
  if (engagementMatches.length >= 4) {
    observations.push({
      kind: "engagement_prompt",
      weight: Math.min(25, 8 + engagementMatches.length),
      evidence: `${engagementMatches.length} visible engagement-oriented controls observed.`,
    });
  }

  const notificationPattern = /turn on notifications|enable notifications|never miss|notify me/i;
  const notificationMatches = interactive.filter((node) =>
    notificationPattern.test((node.textContent || "").trim()),
  );
  if (notificationMatches.length > 0) {
    observations.push({
      kind: "notification_pressure",
      weight: 15,
      evidence: `${notificationMatches.length} notification-prompt control(s) observed.`,
    });
  }

  const viewportRatio =
    window.innerHeight > 0 ? document.documentElement.scrollHeight / window.innerHeight : 0;
  if (viewportRatio >= 6) {
    observations.push({
      kind: "infinite_feed",
      weight: Math.min(25, Math.round(viewportRatio)),
      evidence: `Page height is approximately ${viewportRatio.toFixed(1)} viewports.`,
    });
  }

  const stickyInteractive = interactive.filter((node) => {
    const style = window.getComputedStyle(node);
    return style.position === "fixed" || style.position === "sticky";
  });
  if (stickyInteractive.length >= 2) {
    observations.push({
      kind: "sticky_engagement_control",
      weight: Math.min(20, 6 + stickyInteractive.length * 2),
      evidence: `${stickyInteractive.length} fixed or sticky interactive controls observed.`,
    });
  }

  const score = Math.min(
    100,
    observations.reduce((total, observation) => total + observation.weight, 0),
  );
  const level = score >= 60 ? "high" : score >= 25 ? "moderate" : "low";

  return {
    score,
    level,
    observations,
    boundary: "ATTENTION_SIGNAL != PROOF_OF_PROFILING",
  };
}

function renderAssessment(assessment) {
  resultSection.hidden = false;
  levelNode.textContent = assessment.level.toUpperCase();
  scoreNode.textContent = `${assessment.score} / 100`;
  signalsNode.replaceChildren();

  if (assessment.observations.length === 0) {
    const item = document.createElement("li");
    item.textContent = "No configured attention-capture signals were observed.";
    signalsNode.append(item);
    return;
  }

  for (const observation of assessment.observations) {
    const item = document.createElement("li");
    item.textContent = `${observation.kind}: ${observation.evidence}`;
    signalsNode.append(item);
  }
}

scanButton.addEventListener("click", async () => {
  scanButton.disabled = true;
  scanButton.textContent = "Inspecting…";

  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab?.id) {
      throw new Error("No active tab is available.");
    }

    const [injection] = await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: analyzePage,
    });

    renderAssessment(injection.result);
  } catch (error) {
    resultSection.hidden = false;
    levelNode.textContent = "UNAVAILABLE";
    scoreNode.textContent = "";
    signalsNode.replaceChildren();

    const item = document.createElement("li");
    item.textContent =
      error instanceof Error ? error.message : "Page inspection could not run.";
    signalsNode.append(item);
  } finally {
    scanButton.disabled = false;
    scanButton.textContent = "Inspect this page";
  }
});
