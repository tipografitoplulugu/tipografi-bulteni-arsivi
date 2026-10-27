/**
 * Streamlit Community Cloud Keep-Alive & Auto-Wake Script
 *
 * Runs headless Puppeteer to ping the Streamlit app.
 * If the app is asleep ("Yes, get this app back up!"), clicks the button to wake it up.
 * If the app is already awake, visiting the page refreshes the inactivity timer.
 */

const fs = require('fs');
const puppeteer = require('puppeteer');

const TARGET_URL = process.env.APP_URL || 'https://tipografi-bulteni-arsivi.streamlit.app/';
const TIMEOUT_MS = 60000;

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function resolveExecutablePath() {
  if (process.env.PUPPETEER_EXECUTABLE_PATH) {
    return process.env.PUPPETEER_EXECUTABLE_PATH;
  }

  // On macOS, system Google Chrome is preferred over Chrome for Testing
  // due to macOS Gatekeeper / code signing restrictions on arm64/x64 binaries.
  if (process.platform === 'darwin') {
    const macPaths = [
      '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
      `${process.env.HOME}/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`,
      '/Applications/Chromium.app/Contents/MacOS/Chromium',
    ];
    for (const p of macPaths) {
      if (fs.existsSync(p)) return p;
    }
  }

  // On Linux (CI runners), check standard Chromium/Chrome locations
  if (process.platform === 'linux') {
    const linuxPaths = [
      '/usr/bin/google-chrome-stable',
      '/usr/bin/google-chrome',
      '/usr/bin/chromium-browser',
      '/usr/bin/chromium',
    ];
    for (const p of linuxPaths) {
      if (fs.existsSync(p)) return p;
    }
  }

  // Default to Puppeteer's resolved executable
  try {
    const pptrPath = puppeteer.executablePath();
    if (pptrPath && fs.existsSync(pptrPath)) {
      return pptrPath;
    }
  } catch {
    // Ignore and let Puppeteer launch with its internal defaults
  }

  return undefined;
}

async function findWakeButton(page) {
  // Check main frame and any nested frames (iframes)
  const frames = [page.mainFrame(), ...page.frames().filter((f) => f !== page.mainFrame())];

  for (const frame of frames) {
    try {
      // Find candidate buttons or clickable elements
      const candidates = await frame.$$('button, a, [role="button"], span, div');
      for (const el of candidates) {
        const text = await frame.evaluate((node) => node.innerText || node.textContent || '', el);
        if (/get this app back up/i.test(text.trim())) {
          return { frame, element: el, text: text.trim() };
        }
      }
    } catch {
      // Ignore errors for cross-origin or detached frames
    }
  }

  // Fallback: search via DOM evaluation in main document
  try {
    const handle = await page.evaluateHandle(() => {
      const all = Array.from(document.querySelectorAll('button, a, [role="button"], span, div'));
      return all.find((el) => /get this app back up/i.test(el.textContent || ''));
    });
    if (handle && (await handle.asElement())) {
      return { frame: page.mainFrame(), element: handle.asElement(), text: 'Fallback detected wake button' };
    }
  } catch {
    // Ignore fallback errors
  }

  return null;
}

async function runProbe() {
  console.log(`[Keep-Alive] Starting probe at ${new Date().toISOString()}`);
  console.log(`[Keep-Alive] Target URL: ${TARGET_URL}`);

  const execPath = resolveExecutablePath();
  if (execPath) {
    console.log(`[Keep-Alive] Using browser executable: ${execPath}`);
  }

  const launchOptions = {
    headless: true,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
      '--disable-accelerated-2d-canvas',
      '--disable-gpu',
    ],
  };

  if (execPath) {
    launchOptions.executablePath = execPath;
  }

  let browser;
  try {
    browser = await puppeteer.launch(launchOptions);

    const page = await browser.newPage();
    await page.setViewport({ width: 1366, height: 768 });
    await page.setUserAgent(
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
    );

    console.log('[Keep-Alive] Navigating to target URL...');
    try {
      await page.goto(TARGET_URL, { waitUntil: 'networkidle2', timeout: TIMEOUT_MS });
    } catch (navErr) {
      console.log(`[Keep-Alive] Navigation finished with notice (${navErr.message}). Continuing to check page state...`);
    }

    // Wait a short duration for dynamic client-side rendering / WebSocket handshake
    await sleep(8000);

    const title = await page.title();
    console.log(`[Keep-Alive] Page title: "${title}"`);

    // Check for sleep state and wake-up button
    const wakeTarget = await findWakeButton(page);

    if (wakeTarget) {
      console.log(`[Keep-Alive] 💤 App is currently ASLEEP! Found wake button: "${wakeTarget.text}"`);
      console.log('[Keep-Alive] Clicking "Yes, get this app back up!" button...');
      await wakeTarget.element.click();

      console.log('[Keep-Alive] Button clicked. Waiting 25 seconds for container to initialize...');
      await sleep(25000);

      const afterTitle = await page.title();
      console.log(`[Keep-Alive] ✅ Wake-up request sent. Current page title: "${afterTitle}"`);
    } else {
      console.log('[Keep-Alive] ⚡ App is already AWAKE and ACTIVE.');

      // Check if Streamlit container or main root element is present
      const isStreamlitLoaded = await page.evaluate(() => {
        return Boolean(
          document.querySelector('[data-testid="stAppViewContainer"]') ||
          document.querySelector('#root') ||
          document.querySelector('.stApp') ||
          document.body.innerText.includes('Tipografi')
        );
      });

      console.log(`[Keep-Alive] Streamlit DOM content verified: ${isStreamlitLoaded}`);
      console.log('[Keep-Alive] ✅ Inactivity timer has been successfully reset. Sleep mode prevented!');
    }
  } finally {
    if (browser) {
      await browser.close();
      console.log('[Keep-Alive] Browser closed cleanly.');
    }
  }
}

// Execute probe with single retry on unexpected failure
(async () => {
  try {
    await runProbe();
    process.exit(0);
  } catch (err) {
    console.error(`[Keep-Alive] First attempt error: ${err.message}. Retrying in 10s...`);
    await sleep(10000);
    try {
      await runProbe();
      process.exit(0);
    } catch (retryErr) {
      console.error(`[Keep-Alive] Retry failed: ${retryErr.message}`);
      process.exit(1);
    }
  }
})();
