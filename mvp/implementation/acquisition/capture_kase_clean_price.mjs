// Public, anonymous KASE browser capture for a single instrument page.
// Usage: node capture_kase_clean_price.mjs BIGDb5 ../data/raw/acquisition/DATE
import { createRequire } from "node:module";
if (!process.env.PLAYWRIGHT_NODE_MODULES) {
  throw new Error("Set PLAYWRIGHT_NODE_MODULES to the directory containing the Playwright package.");
}
const require = createRequire(`${process.env.PLAYWRIGHT_NODE_MODULES.replace(/\\/g, "/")}/`);
const { chromium } = require("playwright");
import { mkdir, writeFile } from "node:fs/promises";
import { join } from "node:path";
import { createHash } from "node:crypto";

const [ticker, outputDirectory] = process.argv.slice(2);
if (!ticker || !outputDirectory) throw new Error("Usage: node capture_kase_clean_price.mjs TICKER OUTPUT_DIRECTORY");
const targetUrl = process.env.TARGET_URL ?? `https://kase.kz/ru/investors/bonds/${encodeURIComponent(ticker)}`;
const controlText = process.env.CONTROL_TEXT ?? "чистая цена";
await mkdir(outputDirectory, { recursive: true });

console.error("launching browser");
const browser = await chromium.launch({
  headless: true,
  ...(process.env.PLAYWRIGHT_EXECUTABLE_PATH ? { executablePath: process.env.PLAYWRIGHT_EXECUTABLE_PATH } : {}),
});
const page = await browser.newPage({ viewport: { width: 1440, height: 1100 }, locale: "ru-RU" });
console.error("opening page");
const network = [];
page.on("response", async (response) => {
  const url = response.url();
  if (!url.startsWith("https://kase.kz/")) return;
  if (!url.includes("/api/")) return;
  network.push({ url, status: response.status(), contentType: response.headers()["content-type"] ?? null });
});

await page.goto(targetUrl, { waitUntil: "networkidle", timeout: 60_000 });
console.error(`selecting control: ${controlText}`);
await page.screenshot({ path: join(outputDirectory, `${ticker}.before-selection.png`), fullPage: true });
await writeFile(join(outputDirectory, `${ticker}.before-selection.dom.html`), await page.content(), "utf8");
console.error((await page.locator("body").innerText()).slice(0, 1000));
const clean = page.getByText(controlText, { exact: true }).first();
console.error(`matching controls: ${await page.getByText(controlText, { exact: true }).count()}`);
await clean.click({ timeout: 5_000, force: true });
await page.waitForTimeout(750);

const selection = await clean.evaluate((element) => ({
  tag: element.tagName,
  text: element.textContent?.trim(),
  className: element.className,
  ariaPressed: element.getAttribute("aria-pressed"),
  ariaSelected: element.getAttribute("aria-selected"),
  dataState: element.getAttribute("data-state"),
  outerHTML: element.outerHTML,
}));
const html = await page.content();
const screenshot = join(outputDirectory, `${ticker}.clean-price.png`);
const dom = join(outputDirectory, `${ticker}.clean-price.dom.html`);
const networkPath = join(outputDirectory, `${ticker}.clean-price.network.json`);
await page.screenshot({ path: screenshot, fullPage: true });
await writeFile(dom, html, "utf8");
await writeFile(networkPath, JSON.stringify({
  capturedAtUtc: new Date().toISOString(), ticker, selection,
  network: [...new Map(network.map((row) => [row.url, row])).values()],
}, null, 2) + "\n", "utf8");
console.error("saved capture");
const digest = createHash("sha256").update(await (await import("node:fs/promises")).readFile(screenshot)).digest("hex");
console.log(JSON.stringify({ ticker, screenshot, screenshot_sha256: digest, selection, network_count: network.length }));
await browser.close();
