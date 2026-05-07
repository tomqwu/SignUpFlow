import { chromium } from 'playwright';
import path from 'node:path';
const HTML = 'file:///Users/tomwu/Documents/Projects/SignUpFlow/mobile/prototype/SignUpFlow iOS v2.html';
const OUT = '/Users/tomwu/Documents/Projects/SignUpFlow/mobile/prototype/screenshots/v2';
const sel = '.dev-controls select';

const SHOTS = [
  ['01-login.png',          async (p) => {}],
  ['02-invitation.png',     async (p) => { await p.locator(sel).selectOption('invitation'); }],
  ['03-v-schedule.png',     async (p) => { await p.locator('.role-pill button:has-text("Volunteer")').click(); }],
  ['04-v-assignment.png',   async (p) => { await p.locator('.role-pill button:has-text("Volunteer")').click(); await p.locator(sel).selectOption('v-assignment'); }],
  ['05-v-availability.png', async (p) => { await p.locator('.role-pill button:has-text("Volunteer")').click(); await p.locator('.tab-bar button:has-text("Avail")').click(); }],
  ['06-v-inbox.png',        async (p) => { await p.locator('.role-pill button:has-text("Volunteer")').click(); await p.locator(sel).selectOption('v-inbox'); }],
  ['07-v-profile.png',      async (p) => { await p.locator('.role-pill button:has-text("Volunteer")').click(); await p.locator('.tab-bar button:has-text("Profile")').click(); }],
  ['08-a-dashboard.png',    async (p) => { await p.locator('.role-pill button:has-text("Admin")').click(); }],
  ['09-a-people.png',       async (p) => { await p.locator('.role-pill button:has-text("Admin")').click(); await p.locator('.tab-bar button:has-text("People")').click(); }],
  ['10-a-events.png',       async (p) => { await p.locator('.role-pill button:has-text("Admin")').click(); await p.locator('.tab-bar button:has-text("Events")').click(); }],
  ['11-a-solver.png',       async (p) => { await p.locator('.role-pill button:has-text("Admin")').click(); await p.locator('.tab-bar button:has-text("Solver")').click(); }],
  ['12-a-solution.png',     async (p) => { await p.locator('.role-pill button:has-text("Admin")').click(); await p.locator(sel).selectOption('a-solution'); }],
  ['13-a-compare.png',      async (p) => { await p.locator('.role-pill button:has-text("Admin")').click(); await p.locator(sel).selectOption('a-compare'); }],
  ['14-a-publish.png',      async (p) => { await p.locator('.role-pill button:has-text("Admin")').click(); await p.locator(sel).selectOption('a-publish'); }],
];

const errors = [];
for (const [name, navigate] of SHOTS) {
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width: 560, height: 1080 } });
  const page = await ctx.newPage();
  page.on('pageerror', (e) => errors.push(`${name}: ${e.message}`));
  page.on('console', (m) => { if (m.type() === 'error') errors.push(`${name} console: ${m.text()}`); });
  await page.goto(HTML);
  await page.waitForTimeout(500);
  await navigate(page);
  await page.waitForTimeout(400);
  await page.screenshot({ path: path.join(OUT, name), fullPage: true });
  await browser.close();
  console.log('✓', name);
}
if (errors.length) { console.error('\n❌ Errors:\n' + errors.join('\n')); process.exit(1); }
console.log('\n✓ All 14 captured, 0 errors');
