# Setting Up Playwright for Screenshots

Since I don't have sudo access, **you** need to install the browser dependencies.

## Option 1: Install Dependencies (Recommended)

Run this command on your system:

```bash
sudo apt-get install -y libnspr4 libnss3 libasound2
```

Then Playwright will work and I can take screenshots automatically!

## Option 2: Use Playwright's Installer

```bash
sudo playwright install-deps
```

## After Installing Dependencies

Once you've installed the dependencies, tell me and I'll run:

```bash
poetry run python test_screenshot.py
```

This will automatically:
- Launch a headless browser
- Navigate to http://localhost:8000/
- Login as Sarah
- Take 4 screenshots
- Save them to docs/screenshots/

## Test It Works

After installing dependencies, verify with:

```bash
poetry run playwright --version
poetry run python test_screenshot.py
```

---

**Bottom line:** I have the code ready to take screenshots, but I need YOU to install the system dependencies first since I don't have sudo access.
