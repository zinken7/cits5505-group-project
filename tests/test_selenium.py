# -*- coding: utf-8 -*-
"""
Selenium integration tests for WatchList Hub.

Prerequisites
-------------
1. cd frontend && npm run build   (production assets must exist in app/static/dist/)
2. source .venv/bin/activate
3. pytest tests/test_selenium.py  (run separately from unit tests)

The test suite starts a real Werkzeug HTTP server on port 5055 with a
file-based SQLite database seeded once for the session.
"""
import threading
import time

import pytest
import werkzeug.serving
from selenium import webdriver
from sqlalchemy.pool import NullPool
from selenium.webdriver.chrome.options import Options

# ── Thread-serialized WSGI wrapper ────────────────────────────────────────────

class _SerializedWSGI:
    """Serialize every WSGI call through a single lock.

    Werkzeug threaded=True accepts connections concurrently (so Chrome's burst
    of XHR requests never queues behind a slow navigation) but SQLite's Cython
    extensions are not safe under true parallelism.  This wrapper keeps the
    OS-level accept loop fast while ensuring only one thread runs through Flask
    (and therefore SQLite) at a time.
    """

    def __init__(self, app):
        self._app = app
        self._lock = threading.Lock()

    def __call__(self, environ, start_response):
        path = environ.get("PATH_INFO", "")
        # SocketIO connections are long-lived (long-poll / WebSocket upgrade).
        # They must NOT acquire the lock — they would hold it indefinitely,
        # blocking every subsequent request forever.  Flask-SocketIO's own
        # threading model handles concurrency for /socket.io/* paths.
        if path.startswith("/socket.io/"):
            return self._app(environ, start_response)
        with self._lock:
            return list(self._app(environ, start_response))
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

PORT = 5055
BASE = f"http://127.0.0.1:{PORT}"
TIMEOUT = 10

TEST_EMAIL = "sel@test.com"
TEST_PASSWORD = "Password1!"
TEST_IMDB = "tt1375666"  # Inception

# ── Session fixtures ──────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def selenium_app(tmp_path_factory):
    from app import create_app
    # File-based SQLite is required for thread safety with threaded=True Werkzeug.
    # sqlite:///:memory: causes segfaults when multiple threads access the same
    # in-memory connection concurrently (the JS on auth pages fires many API
    # calls simultaneously, which deadlocks a single-threaded server).
    db_file = str(tmp_path_factory.mktemp("selenium_db") / "test.db")
    app = create_app("testing")
    app.config["VITE_DEV_MODE"] = False
    # Override before any DB access so SQLAlchemy picks up the new URI lazily.
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_file}"
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "connect_args": {"check_same_thread": False},
        "poolclass": NullPool,
    }
    return app


@pytest.fixture(scope="session", autouse=True)
def _seed_db(selenium_app):
    from app.extensions import db
    from app.models.media import Media
    from app.models.user import User

    with selenium_app.app_context():
        db.create_all()
        user = User(username="seluser", email=TEST_EMAIL)
        user.set_password(TEST_PASSWORD)
        db.session.add(user)
        db.session.add_all([
            Media(title="Inception",       media_type="movie",  imdb_id="tt1375666", year=2010, rating=8.8),
            Media(title="Attack on Titan", media_type="anime",  imdb_id="tt2560140", year=2013, rating=9.0),
            Media(title="Breaking Bad",    media_type="tvshow", imdb_id="tt0903747", year=2008, rating=9.5),
        ])
        db.session.commit()

    yield

    with selenium_app.app_context():
        db.drop_all()


@pytest.fixture(scope="session")
def live_server(selenium_app):
    # threaded=True keeps OS-level accept fast so Chrome's burst of XHR calls
    # after login never queues a plain page navigation for 120 s.
    # _SerializedWSGI ensures only one thread enters Flask/SQLite at a time,
    # preventing segfaults in SQLAlchemy's Cython extensions under concurrency.
    server = werkzeug.serving.make_server("127.0.0.1", PORT, _SerializedWSGI(selenium_app), threaded=True)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    time.sleep(0.5)
    yield BASE
    server.shutdown()


@pytest.fixture(scope="session")
def driver(live_server):
    """Headless Chrome, shared across the whole session."""
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1280,800")
    d = webdriver.Chrome(options=opts)
    d.implicitly_wait(2)
    yield d
    d.quit()


# ── Helpers ───────────────────────────────────────────────────────────────────

def w(driver, timeout=TIMEOUT):
    return WebDriverWait(driver, timeout)


def do_login(driver):
    """Log in as the test user; no-op if already authenticated."""
    driver.get(f"{BASE}/login")
    # If already logged in Flask redirects away from /login immediately
    if "/login" not in driver.current_url:
        return
    email_el = w(driver).until(EC.presence_of_element_located((By.NAME, "email")))
    email_el.clear()
    email_el.send_keys(TEST_EMAIL)
    pw_el = driver.find_element(By.NAME, "password")
    pw_el.clear()
    pw_el.send_keys(TEST_PASSWORD)
    driver.find_element(By.CSS_SELECTOR, "button[type=submit]").click()
    w(driver).until(lambda d: "/login" not in d.current_url)


def clear_session(driver):
    """Clear auth state and drain the server request queue before the next test.

    Navigating to a JS-free 404 page forces driver.get() to block until
    Flask finishes all previously queued requests (the serialized wrapper
    only serves the 404 request once the queue ahead of it is empty).
    Deleting cookies afterwards guarantees a clean guest state.
    """
    driver.get(f"{BASE}/no-such-page-drain-queue")  # 404 — no background JS or SocketIO
    driver.delete_all_cookies()


# ── Public page tests ─────────────────────────────────────────────────────────

def test_landing_page_renders(driver):
    driver.get(f"{BASE}/")
    assert "WatchList" in driver.title or "Watchlist" in driver.title
    # Sign-up CTA must be present
    w(driver).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='register']")))


def test_explore_public_slim_topbar(driver):
    clear_session(driver)
    driver.get(f"{BASE}/explore")
    w(driver).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".brand__mark")))
    # Use .btn selector to target visible topbar button, not hidden dropdown links
    assert driver.find_element(By.CSS_SELECTOR, "a.btn[href*='login']").is_displayed()
    assert driver.find_element(By.CSS_SELECTOR, "a.btn[href*='register']").is_displayed()
    # No sidebar for guests
    assert len(driver.find_elements(By.ID, "app-sidebar")) == 0


def test_explore_public_media_cards_load(driver):
    driver.get(f"{BASE}/explore")
    # Wait for JS to replace "Loading…" with actual count
    w(driver).until(
        lambda d: d.find_element(By.ID, "result-count").text.strip()
        not in ("", "Loading…", "Loading...")
    )
    cards = driver.find_elements(By.CSS_SELECTOR, "#results-grid .mcard")
    assert len(cards) > 0, "Explore grid must have at least one media card"


def test_explore_type_filter_works(driver):
    driver.get(f"{BASE}/explore")
    w(driver).until(lambda d: "Loading" not in d.find_element(By.ID, "result-count").text)
    driver.find_element(By.CSS_SELECTOR, "#type-filter button[data-type='movie']").click()
    w(driver).until(lambda d: "Loading" not in d.find_element(By.ID, "result-count").text)
    assert len(driver.find_elements(By.CSS_SELECTOR, "#results-grid .mcard")) > 0


def test_item_detail_public_hydrates_title(driver):
    driver.get(f"{BASE}/items/{TEST_IMDB}")
    w(driver).until(
        lambda d: d.find_element(By.CSS_SELECTOR, "[data-field='title']").text.strip() != ""
    )
    assert "Inception" in driver.find_element(By.CSS_SELECTOR, "[data-field='title']").text


def test_item_detail_public_shows_login_cta(driver):
    driver.get(f"{BASE}/items/{TEST_IMDB}")
    w(driver).until(lambda d: d.find_element(By.CSS_SELECTOR, "[data-field='title']").text.strip() != "")
    # Guest detail page shows a Log In CTA button (not watchlist controls)
    assert driver.find_element(By.CSS_SELECTOR, "a.btn[href*='login']").is_displayed()
    assert len(driver.find_elements(By.CSS_SELECTOR, "[data-action='add-to-watchlist']")) == 0


def test_custom_404_page(driver):
    driver.get(f"{BASE}/this-does-not-exist-xyz-404")
    w(driver).until(EC.presence_of_element_located((By.CSS_SELECTOR, "img[alt='404 illustration']")))
    assert driver.find_element(By.CSS_SELECTOR, "a[href*='explore']").is_displayed()


# ── Auth flow tests ───────────────────────────────────────────────────────────

def test_register_new_user(driver):
    clear_session(driver)
    driver.get(f"{BASE}/register")
    w(driver).until(EC.presence_of_element_located((By.NAME, "username"))).send_keys("newseluser")
    driver.find_element(By.NAME, "email").send_keys("newsel@test.com")
    driver.find_element(By.NAME, "password").send_keys("Password1!")
    driver.find_element(By.CSS_SELECTOR, "button[type=submit]").click()
    # Successful registration redirects away from /register
    w(driver).until(lambda d: "/register" not in d.current_url)


def test_login_redirects_away_from_login(driver):
    clear_session(driver)
    do_login(driver)
    assert "/login" not in driver.current_url


def test_logout_clears_session(driver):
    clear_session(driver)
    do_login(driver)
    # Test the actual logout UI
    driver.get(f"{BASE}/logout")
    btn = w(driver).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type=submit]")))
    btn.click()
    w(driver).until(lambda d: "/logout" not in d.current_url)
    # Protected page must now redirect to login
    driver.get(f"{BASE}/dashboard")
    w(driver).until(lambda d: "/login" in d.current_url)


# ── Authenticated page tests ──────────────────────────────────────────────────

def test_explore_auth_shows_sidebar(driver):
    clear_session(driver)
    do_login(driver)
    driver.get(f"{BASE}/explore")
    w(driver).until(EC.presence_of_element_located((By.ID, "app-sidebar")))
    assert driver.find_element(By.ID, "app-sidebar").is_displayed()


def test_explore_auth_media_cards_load(driver):
    driver.get(f"{BASE}/explore")
    w(driver).until(lambda d: "Loading" not in d.find_element(By.ID, "result-count").text)
    assert len(driver.find_elements(By.CSS_SELECTOR, "#results-grid .mcard")) > 0


def test_dashboard_watchlist_tabs_visible(driver):
    driver.get(f"{BASE}/dashboard")
    w(driver).until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-tab='watching']")))
    assert driver.find_element(By.CSS_SELECTOR, "[data-tab='planned']").is_displayed()
    assert driver.find_element(By.CSS_SELECTOR, "[data-tab='completed']").is_displayed()


def test_profile_me_page_loads(driver):
    driver.get(f"{BASE}/profile/me")
    w(driver).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".avatar")))
    assert driver.find_element(By.CSS_SELECTOR, "[data-tab='watching']").is_displayed()


def test_item_detail_auth_hydrates(driver):
    driver.get(f"{BASE}/items/{TEST_IMDB}")
    w(driver).until(lambda d: d.find_element(By.CSS_SELECTOR, "[data-field='title']").text.strip() != "")
    assert "Inception" in driver.find_element(By.CSS_SELECTOR, "[data-field='title']").text


def test_item_detail_add_to_watchlist_shows_toast(driver):
    driver.get(f"{BASE}/items/{TEST_IMDB}")
    w(driver).until(lambda d: d.find_element(By.CSS_SELECTOR, "[data-field='title']").text.strip() != "")

    add_btns = driver.find_elements(By.CSS_SELECTOR, "[data-action='add-to-watchlist']")
    if add_btns and add_btns[0].is_displayed():
        # JS-click to avoid ElementClickInterceptedException from overlapping elements.
        driver.execute_script("arguments[0].scrollIntoView({block:'center'}); arguments[0].click();", add_btns[0])
        # After a successful add the button label changes to "Remove from Watchlist"
        # (the JS calls applyState() once the PUT 200 returns — no separate toast).
        w(driver).until(
            lambda d: "Remove" in d.find_element(
                By.CSS_SELECTOR, "[data-action='add-to-watchlist'] [data-field='action-label']"
            ).text
        )
    else:
        # Already in watchlist — status control must be present instead
        w(driver).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#status-control")))


def test_item_detail_status_buttons_after_add(driver):
    driver.get(f"{BASE}/items/{TEST_IMDB}")
    w(driver).until(lambda d: d.find_element(By.CSS_SELECTOR, "[data-field='title']").text.strip() != "")
    # After adding, the status control (Watching/Planned/Completed) must be visible
    w(driver).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#status-control")))


def test_topbar_search_shows_dropdown(driver):
    driver.get(f"{BASE}/explore")
    w(driver).until(EC.presence_of_element_located((By.ID, "app-sidebar")))

    search_input = w(driver).until(EC.element_to_be_clickable((By.ID, "tsearch-input")))
    search_input.click()
    search_input.send_keys("Inception")

    # hidden attribute is removed by JS when results are ready
    w(driver).until(
        lambda d: d.find_element(By.ID, "tsearch-drop").get_attribute("hidden") is None
    )
    items = driver.find_elements(By.CSS_SELECTOR, "#tsearch-results .tsearch-item")
    assert len(items) > 0, "Search dropdown must contain at least one result"


def test_categories_page_loads(driver):
    driver.get(f"{BASE}/categories")
    w(driver).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".mcard, [class*='genre']")))
    assert "Drama" in driver.page_source or "Categories" in driver.page_source
