"""The web UI fits the screen it is on: a phone, a tablet or a desktop.

It used to be one phone-width column centred on every screen, with a phone tab
bar at the bottom even on a desktop monitor. The phone layout stays as it was,
close to the parked Flutter app; wider screens get room to work with. These
tests measure the rendered pages, as the demo accounts, in every engine.
"""

from __future__ import annotations

import pytest

from tests.e2e.conftest import (
    DEMO_ADMIN,
    DEMO_MUSICIAN,
    ENGINES,
    assert_page_health,
    track_page_health,
)

PHONE = {"width": 390, "height": 844}
TABLET = {"width": 820, "height": 1180}
DESKTOP = {"width": 1440, "height": 900}

ADMIN_PAGES = ["/a/dashboard", "/a/assignments", "/a/events", "/a/people", "/a/analytics"]
MEMBER_PAGES = ["/v/schedule", "/v/open", "/v/availability"]

#: How many lines of text an element's label occupies.
_LINE_COUNT = """(els) => els.map((el) => {
    const range = document.createRange();
    range.selectNodeContents(el);
    // Rects on one line differ by a few pixels (an arrow glyph sits higher),
    // so group tops within half a line height.
    const half = parseFloat(getComputedStyle(el).fontSize) * 0.6;
    const lines = [];
    for (const r of range.getClientRects()) {
        if (r.width && !lines.some((top) => Math.abs(top - r.top) < half)) lines.push(r.top);
    }
    return lines.length;
})"""

_BOX = "(el) => { const r = el.getBoundingClientRect(); return [r.x, r.y, r.width, r.height]; }"


def _open(engine_browser, engine, demo_base, demo_sessions, account, viewport):
    context = engine_browser(engine).new_context(
        viewport=viewport, storage_state=demo_sessions[account] if account else None
    )
    track_page_health(context)
    return context, context.new_page()


def _go(page, url):
    page.goto(url)
    page.wait_for_load_state("networkidle")


def _no_sideways_scroll(page, where):
    width = page.evaluate("document.documentElement.scrollWidth")
    viewport = page.evaluate("window.innerWidth")
    assert width <= viewport + 1, f"{where} scrolls sideways ({width}px in {viewport}px)"


def _box(page, selector):
    return page.eval_on_selector(selector, _BOX)


@pytest.mark.parametrize("engine", ENGINES)
def test_phone_keeps_the_app_layout(engine, engine_browser, demo_base, demo_sessions):
    context, page = _open(engine_browser, engine, demo_base, demo_sessions, DEMO_ADMIN, PHONE)
    try:
        for path in ADMIN_PAGES:
            _go(page, f"{demo_base}{path}")
            where = f"{engine} phone {path}"
            _no_sideways_scroll(page, where)
            x, _y, width, height = _box(page, ".tab-bar")
            assert width >= PHONE["width"] - 2 and height < 100, f"{where}: no bottom tab bar"
            _x, _y, content, _h = _box(page, ".scroll")
            assert content >= PHONE["width"] - 2, f"{where}: content narrower than the phone"
        assert_page_health(context)
    finally:
        context.close()


@pytest.mark.parametrize("engine", ENGINES)
def test_tablet_has_no_sideways_scroll(engine, engine_browser, demo_base, demo_sessions):
    context, page = _open(engine_browser, engine, demo_base, demo_sessions, DEMO_ADMIN, TABLET)
    try:
        for path in ADMIN_PAGES:
            _go(page, f"{demo_base}{path}")
            _no_sideways_scroll(page, f"{engine} tablet {path}")
            _x, _y, content, _h = _box(page, ".scroll")
            assert content >= 700, f"{engine} tablet {path}: content only {content}px wide"
        assert_page_health(context)
    finally:
        context.close()


@pytest.mark.parametrize("engine", ENGINES)
def test_desktop_admin_uses_a_sidebar_and_the_width(
    engine, engine_browser, demo_base, demo_sessions
):
    context, page = _open(engine_browser, engine, demo_base, demo_sessions, DEMO_ADMIN, DESKTOP)
    try:
        for path in ADMIN_PAGES:
            _go(page, f"{demo_base}{path}")
            where = f"{engine} desktop {path}"
            _no_sideways_scroll(page, where)
            side_x, _side_y, side_w, side_h = _box(page, ".tab-bar")
            main_x, _main_y, main_w, _main_h = _box(page, ".scroll")
            assert side_w < 300 and side_h >= DESKTOP["height"] * 0.8, f"{where}: no sidebar"
            assert side_x + side_w <= main_x + 1, f"{where}: sidebar overlaps the content"
            assert main_w >= 900, f"{where}: content only {main_w}px wide"
        assert_page_health(context)
    finally:
        context.close()


@pytest.mark.parametrize("engine", ENGINES)
def test_desktop_dashboard_lays_its_numbers_out_in_one_row(
    engine, engine_browser, demo_base, demo_sessions
):
    context, page = _open(engine_browser, engine, demo_base, demo_sessions, DEMO_ADMIN, DESKTOP)
    try:
        _go(page, f"{demo_base}/a/dashboard")
        tops = page.eval_on_selector_all(
            ".kpi", "(els) => els.map((el) => Math.round(el.getBoundingClientRect().top))"
        )
        assert len(tops) == 4 and len(set(tops)) == 1, f"{engine}: KPI rows {tops}"
        assert_page_health(context)
    finally:
        context.close()


@pytest.mark.parametrize("engine", ENGINES)
def test_desktop_volunteer_pages_widen_with_a_sidebar(
    engine, engine_browser, demo_base, demo_sessions
):
    context, page = _open(engine_browser, engine, demo_base, demo_sessions, DEMO_MUSICIAN, DESKTOP)
    try:
        for path in MEMBER_PAGES:
            _go(page, f"{demo_base}{path}")
            where = f"{engine} desktop {path}"
            _no_sideways_scroll(page, where)
            _sx, _sy, side_w, side_h = _box(page, ".tab-bar")
            assert side_w < 300 and side_h >= DESKTOP["height"] * 0.8, f"{where}: no sidebar"
            _mx, _my, main_w, _mh = _box(page, ".scroll")
            assert main_w >= 640, f"{where}: content only {main_w}px wide"
        assert_page_health(context)
    finally:
        context.close()


@pytest.mark.parametrize("engine", ENGINES)
def test_desktop_sign_in_stays_a_narrow_card(engine, engine_browser, demo_base):
    context = engine_browser(engine).new_context(viewport=DESKTOP)
    track_page_health(context)
    try:
        page = context.new_page()
        _go(page, f"{demo_base}/auth/login")
        _no_sideways_scroll(page, f"{engine} desktop sign-in")
        _x, _y, form_w, _h = _box(page, "form")
        assert form_w <= 560, f"{engine}: sign-in form stretched to {form_w}px"
        assert_page_health(context)
    finally:
        context.close()


def _tops(page, selector):
    return page.eval_on_selector_all(
        selector, "(els) => els.map((el) => Math.round(el.getBoundingClientRect().top))"
    )


@pytest.mark.parametrize("engine", ENGINES)
def test_desktop_admin_content_is_arranged_for_the_width(
    engine, engine_browser, demo_base, demo_sessions
):
    context, page = _open(engine_browser, engine, demo_base, demo_sessions, DEMO_ADMIN, DESKTOP)
    try:
        _go(page, f"{demo_base}/a/dashboard")
        links = _tops(page, ".dash-links > .btn")
        assert len(links) >= 4 and len(set(links)) == 1, f"{engine}: dashboard links {links}"
        columns = _tops(page, ".dash-columns > *")
        assert len(columns) == 2 and len(set(columns)) == 1, f"{engine}: dashboard columns"

        _go(page, f"{demo_base}/a/events")
        actions = page.eval_on_selector(
            ".event-row",
            "(row) => [...row.querySelectorAll('.event-actions .btn')]"
            ".map((el) => Math.round(el.getBoundingClientRect().top))",
        )
        assert actions and len(set(actions)) == 1, f"{engine}: event actions stack {actions}"
        _x, _y, button_w, _h = _box(page, ".scroll > .btn, .scroll .btn-primary")
        assert button_w < 600, f"{engine}: a page button stretched to {button_w}px"

        _go(page, f"{demo_base}/a/assignments")
        heights = page.eval_on_selector_all(
            ".assignment-row",
            "(els) => els.slice(0, 5).map((el) => el.getBoundingClientRect().height)",
        )
        assert heights and max(heights) < 80, f"{engine}: assignment rows {heights}"
        assert_page_health(context)
    finally:
        context.close()


@pytest.mark.parametrize("engine", ENGINES)
def test_sidebar_reaches_every_admin_section_on_desktop_only(
    engine, engine_browser, demo_base, demo_sessions
):
    sections = ["/a/assignments", "/a/swaps", "/a/analytics", "/a/teams", "/a/recurring"]
    for viewport, visible in ((DESKTOP, True), (PHONE, False)):
        context, page = _open(
            engine_browser, engine, demo_base, demo_sessions, DEMO_ADMIN, viewport
        )
        try:
            _go(page, f"{demo_base}/a/assignments")
            for href in sections:
                link = page.locator(f".tab-bar a[href='{href}']")
                assert link.count() == 1, f"{engine}: sidebar has no {href}"
                assert link.is_visible() is visible, f"{engine} {viewport}: {href} visibility"
            if visible:
                current = page.locator(".tab-bar a[href='/a/assignments']")
                assert "active" in (current.get_attribute("class") or "")
                shadowed = page.locator(".tab-bar a.active:not(.shadowed)")
                assert shadowed.count() == 1, f"{engine}: more than one item looks current"
            assert_page_health(context)
        finally:
            context.close()


@pytest.mark.parametrize("engine", ENGINES)
def test_dashboard_shortcuts_keep_their_labels_on_one_line(
    engine, engine_browser, demo_base, demo_sessions
):
    """The longest shortcut wrapped onto two left-aligned lines in a quarter column."""
    for width in (1024, 1280, 1440):
        viewport = {"width": width, "height": 900}
        context, page = _open(
            engine_browser, engine, demo_base, demo_sessions, DEMO_ADMIN, viewport
        )
        try:
            _go(page, f"{demo_base}/a/dashboard")
            _no_sideways_scroll(page, f"{engine} {width}px dashboard")
            # Grid rows stretch every button to the same height, so count the
            # label's own lines of text instead.
            lines = page.eval_on_selector_all(".dash-links > .btn", _LINE_COUNT)
            assert max(lines) == 1, f"{engine} {width}px: a shortcut label wrapped {lines}"
            assert_page_health(context)
        finally:
            context.close()


@pytest.mark.parametrize("engine", ENGINES)
@pytest.mark.parametrize("viewport", [PHONE, DESKTOP], ids=["phone", "desktop"])
def test_checkboxes_sit_next_to_their_labels(
    engine, viewport, engine_browser, demo_base, demo_sessions
):
    """A checkbox inside a form field took the whole row and pushed its label
    to the far edge, on phones and, far more visibly, on desktops."""
    context, page = _open(engine_browser, engine, demo_base, demo_sessions, DEMO_ADMIN, viewport)
    try:
        _go(page, f"{demo_base}/a/recurring")
        page.click("text=New series")
        page.wait_for_selector("input[name=selected_days]", state="visible")
        # From the checkbox's left edge to its label: a stretched checkbox
        # carries its label to the far side of the field.
        spans = page.eval_on_selector_all(
            "input[name=selected_days]",
            "(els) => els.map((box) => box.nextElementSibling.getBoundingClientRect().left"
            " - box.getBoundingClientRect().left)",
        )
        assert spans and max(spans) < 60, f"{engine} {viewport}: checkbox to label {spans}"
        assert_page_health(context)
    finally:
        context.close()


@pytest.mark.parametrize("engine", ENGINES)
def test_desktop_forms_keep_a_readable_width(engine, engine_browser, demo_base, demo_sessions):
    context, page = _open(engine_browser, engine, demo_base, demo_sessions, DEMO_ADMIN, DESKTOP)
    try:
        for path, opener in (("/a/recurring", "text=New series"), ("/a/settings", None)):
            _go(page, f"{demo_base}{path}")
            if opener:
                page.click(opener)
                page.wait_for_selector("form[hx-post='/a/recurring/create']", state="visible")
            widths = page.eval_on_selector_all(
                ".scroll form:not([hidden])",
                "(els) => els.filter((el) => el.offsetParent)"
                ".map((el) => el.getBoundingClientRect().width)",
            )
            assert widths and max(widths) <= 760, f"{engine} {path}: form widths {widths}"
        assert_page_health(context)
    finally:
        context.close()
