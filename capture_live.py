import asyncio
from playwright.async_api import async_playwright
import time
import subprocess

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={'width': 1280, 'height': 800})
        await page.goto("http://127.0.0.1:3000")

        # Click Live
        await page.click("#modeLiveBtn")
        # Ensure #livePanel is visible
        await page.wait_for_selector("#livePanel", state="visible")
        # Click Connect
        await page.click("#connectBtn")

        print("Waiting for trades...")
        await page.wait_for_function("parseInt(document.getElementById('trV').textContent) > 20", timeout=20000)
        await asyncio.sleep(2)
        await page.screenshot(path="live_demo.png")
        print("Screenshot saved to live_demo.png")
        await browser.close()

if __name__ == "__main__":
    ws = subprocess.Popen(["bun", "run", "mock_server.ts"])
    http = subprocess.Popen(["python3", "-m", "http.server", "3000", "--bind", "127.0.0.1"])
    time.sleep(3)
    try:
        asyncio.run(run())
    finally:
        ws.terminate()
        http.terminate()
