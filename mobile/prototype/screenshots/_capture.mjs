// Captures all 14 screens by clicking the dev controls + tab bar.
// Run: node mobile/prototype/screenshots/_capture.mjs

import { chromium } from 'playwright';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const HTML = 'file:///Users/tomwu/Documents/Projects/SignUpFlow/mobile/prototype/SignUpFlow iOS v1.html';
const OUTDIR = '/Users/tomwu/Documents/Projects/SignUpFlow/mobile/prototype/screenshots';

// Each entry: navigate from a fresh page (default = login).
// 3 vol tabs (Schedule/Availability/Profile), 4 admin tabs (Dashboard/People/Events/Solver).
// Inbox + More are reachable only via the dev jump-to dropdown.
const sel = '.dev-controls select';
const SHOTS = [
  ['01-login.png',          async (p) => {}],
  ['02-v-schedule.png',     async (p) => { await p.locator('.role-pill button:has-text("Volunteer")').click(); }],
  ['03-v-availability.png', async (p) => { await p.locator('.role-pill button:has-text("Volunteer")').click(); await p.locator('.tab-bar button:has-text("Availability")').click(); }],
  ['04-v-profile.png',      async (p) => { await p.locator('.role-pill button:has-text("Volunteer")').click(); await p.locator('.tab-bar button:has-text("Profile")').click(); }],
  ['05-v-inbox.png',        async (p) => { await p.locator('.role-pill button:has-text("Volunteer")').click(); await p.locator(sel).selectOption('v-inbox'); }],
  ['06-a-dashboard.png',    async (p) => { await p.locator('.role-pill button:has-text("Admin")').click(); }],
  ['07-a-people.png',       async (p) => { await p.locator('.role-pill button:has-text("Admin")').click(); await p.locator('.tab-bar button:has-text("People")').click(); }],
  ['08-a-events.png',       async (p) => { await p.locator('.role-pill button:has-text("Admin")').click(); await p.locator('.tab-bar button:has-text("Events")').click(); }],
  ['09-a-solver.png',       async (p) => { await p.locator('.role-pill button:has-text("Admin")').click(); await p.locator('.tab-bar button:has-text("Solver")').click(); }],
  ['10-a-solution.png',     async (p) => { await p.locator('.role-pill button:has-text("Admin")').click(); await p.locator(sel).selectOption('a-solution'); }],
  ['11-a-compare.png',      async (p) => { await p.locator('.role-pill button:has-text("Admin")').click(); await p.locator(sel).selectOption('a-compare'); }],
  ['12-a-publish.png',      async (p) => { await p.locator('.role-pill button:has-text("Admin")').click(); await p.locator(sel).selectOption('a-publish'); }],
];

const errors = [];

for (const [name, navigate] of SHOTS) {
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width: 560, height: 1080 } });
  const page = await ctx.newPage();
  page.on('pageerror', (e) => errors.push(`${name}: ${e.message}`));
  page.on('console', (msg) => { if (msg.type() === 'error') errors.push(`${name} console: ${msg.text()}`); });
  await page.goto(HTML);
  await page.waitForTimeout(500);
  await navigate(page);
  await page.waitForTimeout(400);
  await page.screenshot({ path: path.join(OUTDIR, name), fullPage: true });
  await browser.close();
  console.log('✓', name);
}

if (errors.length) {
  console.error('\n❌ Errors:\n' + errors.join('\n'));
  process.exit(1);
}
console.log('\n✓ All 10 screens captured, 0 errors');
