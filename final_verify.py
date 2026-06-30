
import asyncio
from playwright.async_api import async_playwright
import os

async def verify():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context(viewport={'width': 1600, 'height': 900})
        page = await context.new_page()

        path = os.path.abspath("index.html")
        await page.goto(f"file://{path}")

        # Wait for simulation to start
        await page.wait_for_timeout(2000)

        # Take screenshot of 1x1
        await page.screenshot(path="final_1x1.png")
        print("Captured final_1x1.png")

        # Switch to 2x2
        await page.click("button[data-layout='2x2']")
        await page.wait_for_timeout(1000)
        await page.screenshot(path="final_2x2.png")
        print("Captured final_2x2.png")

        # Click on second chart to activate it
        charts = await page.query_selector_all(".chart-wrapper")
        if len(charts) > 1:
            await charts[1].click()
            await page.wait_for_timeout(500)
            await page.screenshot(path="final_2x2_active_2.png")
            print("Captured final_2x2_active_2.png")

        # Verify Sidebar Sync
        # Change Intensity on active chart (chart 1)
        await page.fill("#hmIntensity", "2.5")
        # Need to trigger input event if it doesn't automatically
        await page.evaluate("document.getElementById('hmIntensity').dispatchEvent(new Event('input'))")
        await page.wait_for_timeout(500)

        # Switch back to first chart
        await charts[0].click()
        await page.wait_for_timeout(500)
        # Check if intensity slider reverted to 1.2 (default)
        intensity = await page.input_value("#hmIntensity")
        print(f"Intensity on Chart 0: {intensity}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(verify())
