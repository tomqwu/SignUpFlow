from playwright.sync_api import sync_playwright

def take_screenshots():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()
        
        print("📸 Taking Rostio screenshots...")
        
        # Screenshot 1: Welcome screen
        page.goto('http://localhost:8000/')
        page.wait_for_load_state('networkidle')
        page.screenshot(path='docs/screenshots/01-welcome.png', full_page=True)
        print("✅ 01-welcome.png")
        
        # Screenshot 2: Click to show login
        login_link = page.locator('text=Already have an account')
        if login_link.is_visible():
            login_link.click()
            page.wait_for_timeout(1000)
            page.screenshot(path='docs/screenshots/02-login.png', full_page=True)
            print("✅ 02-login.png")
        
        # Login manually by setting localStorage (skip the hidden form)
        page.evaluate("""
            localStorage.setItem('roster_user', JSON.stringify({
                id: 'person_sarah_1759357429',
                name: 'Sarah Johnson',
                email: 'sarah@grace.church',
                roles: ['worship-leader', 'vocalist']
            }));
            localStorage.setItem('roster_org', JSON.stringify({
                id: 'grace-church',
                name: 'Grace Community Church',
                config: {}
            }));
        """)
        
        # Reload to trigger login
        page.goto('http://localhost:8000/')
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(2000)
        
        # Screenshot 3: Calendar view (logged in)
        page.screenshot(path='docs/screenshots/03-calendar.png', full_page=True)
        print("✅ 03-calendar.png")
        
        # Screenshot 4: Click View Schedule
        schedule_btn = page.locator('text=View Schedule').first
        if schedule_btn.is_visible():
            schedule_btn.click()
            page.wait_for_timeout(1000)
            page.screenshot(path='docs/screenshots/04-schedule.png', full_page=True)
            print("✅ 04-schedule.png")
        
        browser.close()
        print("\n✅ All screenshots saved to docs/screenshots/")

if __name__ == '__main__':
    take_screenshots()
