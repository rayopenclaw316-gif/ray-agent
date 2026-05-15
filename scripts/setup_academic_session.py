#!/usr/bin/env python3
"""
第一次執行此腳本來儲存 ScienceDirect 登入 session。
之後 academic_fetch.py 會自動重用這個 session。
"""
import os
import asyncio
from dotenv import load_dotenv
from playwright.async_api import async_playwright

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

EMAIL = os.getenv('ACADEMIC_EMAIL')
PASSWORD = os.getenv('ACADEMIC_PASSWORD')
SESSION_FILE = os.path.join(os.path.dirname(__file__), 'academic_session.json')


async def main():
    async with async_playwright() as p:
        # 使用系統 Chrome 繞過 Cloudflare bot 偵測
        browser = await p.chromium.launch(
            headless=False,
            channel='chrome',
        )
        ctx = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
        )
        page = await ctx.new_page()

        print("正在開啟 ScienceDirect 登入頁面...")
        await page.goto('https://www.sciencedirect.com/user/login')
        # 等待登入表單出現（無論在哪個 URL）
        await page.wait_for_timeout(5000)
        await page.screenshot(path='/Users/rayopenclaw/ray-agent/debug-login.png')
        print(f"截圖已存，目前 URL：{page.url}")

        # 填入 email
        await page.get_by_role('textbox').first.fill(EMAIL)
        await page.keyboard.press('Enter')
        await page.wait_for_timeout(2000)

        # 填入密碼
        await page.wait_for_selector('input[type="password"]', timeout=15000)
        await page.fill('input[type="password"]', PASSWORD)
        await page.get_by_role('button', name='登入').click()
        await page.wait_for_load_state('networkidle', timeout=20000)

        print(f"登入完成，目前頁面：{page.url}")

        # 儲存 session
        await ctx.storage_state(path=SESSION_FILE)
        print(f"Session 已儲存到：{SESSION_FILE}")

        await browser.close()


if __name__ == '__main__':
    asyncio.run(main())
