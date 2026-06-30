import asyncio
from playwright.async_api import async_playwright
import time

async def test_time_and_volume():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        import os
        path = os.path.abspath("index.html")
        await page.goto(f"file://{path}")

        # Switch to LIVE mode to use processLiveData
        await page.click("#modeLiveBtn")

        # Test Case 1: Millisecond timestamp
        print("Testing millisecond timestamp...")
        now_ms = int(time.time() * 1000)
        await page.evaluate(f"activeChart.processLiveData({{ltp: 24000, volume: 1000, timestamp: {now_ms}}})")
        chart_time = await page.evaluate("activeChart.bars[activeChart.bars.length-1].time")
        print(f"Input ms: {now_ms}, Chart time (sec): {chart_time}")
        if chart_time == now_ms // 1000:
            print("SUCCESS: ms timestamp parsed correctly.")
        else:
            print("FAILURE: ms timestamp parsed incorrectly.")

        # Test Case 2: Incremental volume within same second (different trade time)
        print("Testing volume delta within same second...")
        await page.evaluate(f"activeChart.processLiveData({{ltp: 24001, volume: 1100, timestamp: {now_ms}, ltt: {now_ms+1}}})")
        trade_count = await page.evaluate("activeChart.trades.length")
        cvd = await page.evaluate("activeChart.cvd")
        print(f"Trades: {trade_count}, CVD: {cvd}")
        if trade_count == 1 and cvd == 100:
            print("SUCCESS: Volume delta detected correctly.")
        else:
            print(f"FAILURE: Volume delta NOT detected correctly. Trades: {trade_count}, CVD: {cvd}")

        # Test Case 3: Backwards time prevention
        print("Testing backwards time prevention...")
        past_ms = now_ms - 5000
        await page.evaluate(f"activeChart.processLiveData({{ltp: 24002, volume: 1200, timestamp: {past_ms}}})")
        final_time = await page.evaluate("activeChart.bars[activeChart.bars.length-1].time")
        print(f"Past ms: {past_ms}, Final chart time: {final_time}")
        if final_time >= chart_time:
            print("SUCCESS: Time did not go backwards.")
        else:
            print("FAILURE: Time went backwards.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_time_and_volume())
