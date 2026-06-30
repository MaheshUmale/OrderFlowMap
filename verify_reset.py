import asyncio
from playwright.async_api import async_playwright

async def run_verification():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        # Load the local index.html
        import os
        path = os.path.abspath("index.html")
        await page.goto(f"file://{path}")

        print("Initial state: SIM mode active.")

        # Check if bars are populated (simulated history)
        bars_count = await page.evaluate("activeChart.bars.length")
        print(f"Bars count: {bars_count}")

        # Switch to LIVE
        print("Switching to LIVE mode...")
        await page.click("#modeLiveBtn")

        # Check if bars are cleared
        bars_count_after = await page.evaluate("activeChart.bars.length")
        print(f"Bars count after switch to LIVE: {bars_count_after}")

        if bars_count_after == 0:
            print("SUCCESS: Data cleared on switch to LIVE.")
        else:
            print(f"FAILURE: Data NOT cleared on switch to LIVE. Count: {bars_count_after}")

        # Switch back to SIM
        print("Switching back to SIM mode...")
        await page.click("#modeSimBtn")

        # In SIM mode, it seeds history immediately after loop starts if it was reset?
        # Actually, resetData() clears it, but the loop continues.
        # Wait a bit for the loop to add at least one bar
        await asyncio.sleep(1)
        bars_count_sim = await page.evaluate("activeChart.bars.length")
        print(f"Bars count after switch back to SIM (and 1s wait): {bars_count_sim}")

        # Check other reset fields
        cvd = await page.evaluate("activeChart.cvd")
        print(f"CVD after reset: {cvd}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_verification())
