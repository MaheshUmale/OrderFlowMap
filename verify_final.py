import asyncio
from playwright.async_api import async_playwright
import os

async def verify_final():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.set_viewport_size({"width": 1400, "height": 1000})

        path = "file://" + os.path.abspath("index.html")
        await page.goto(path)
        await page.wait_for_timeout(2000)

        # Expand Local Storage
        await page.evaluate("""
            const h4 = Array.from(document.querySelectorAll('h4')).find(x => x.textContent.includes('Local Storage'));
            if (h4) h4.parentElement.classList.remove('collapsed');
        """)

        # Switch to Live and Inject a trade
        await page.click("#modeLiveBtn")
        await page.evaluate("""
            (async () => {
                const inst = window.activeChart;
                const now = Math.floor(Date.now() / 1000);
                // First tick to set BBO
                inst.processLiveData({
                    ltp: 25000, volume: 1000, last_qty: 0, timestamp: now,
                    depth: { buy: [{price: 24995, quantity: 500}], sell: [{price: 25005, quantity: 500}] }
                });
                // Second tick to trigger Buy trade at Ask
                inst.processLiveData({
                    ltp: 25005, volume: 1150, last_qty: 150, timestamp: now + 1,
                    depth: { buy: [{price: 24995, quantity: 500}], sell: [{price: 25005, quantity: 350}] }
                });
                if (window.updateDBStats) await window.updateDBStats();
            })()
        """)
        await page.wait_for_timeout(1000)

        # Click 2x2 layout
        await page.click("[data-layout='2x2']")
        await page.wait_for_timeout(500)

        screenshot_path = os.path.abspath("final_verification.png")
        await page.screenshot(path=screenshot_path)
        print(f"Final screenshot saved to {screenshot_path}")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(verify_final())
