#!/usr/bin/env python3
"""
透過學校 VPN 機構 IP 抓取論文摘要並下載 PDF
用法：python3 academic_fetch.py <URL> [--pdf]
"""
import sys
import os
import asyncio
import re

PDF_DIR = os.path.join(os.path.dirname(__file__), 'papers')
os.makedirs(PDF_DIR, exist_ok=True)


def safe_filename(title: str) -> str:
    return re.sub(r'[^\w\s-]', '', title).strip()[:80] + '.pdf'


async def fetch_sciencedirect(url: str, download_pdf: bool = False) -> str:
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            accept_downloads=True,
        )
        page = await ctx.new_page()
        await page.goto(url, wait_until='domcontentloaded', timeout=60000)
        await page.wait_for_timeout(4000)

        result = await page.evaluate("""() => {
            const title = document.querySelector('h1.title-text')?.innerText || document.title;
            const abstract = document.querySelector('.abstract')?.innerText
                          || document.querySelector('[class*="abstract"]')?.innerText
                          || document.querySelector('#abstracts')?.innerText || '';
            const keywords = document.querySelector('.keyword')?.innerText
                           || document.querySelector('.keywords')?.innerText || '';
            const authors = Array.from(document.querySelectorAll('.author-name'))
                           .map(a => a.innerText).join(', ');
            const journal = document.querySelector('.publication-volume .anchor')?.innerText || '';
            const pdfHref = document.querySelector('a.pdf-download-btn-link, a[href*="/pdfdirect/"], a[data-aa-name="btn-download-pdf"]')?.href || '';
            return { title, abstract, keywords, authors, journal, pdfHref };
        }""")

        pdf_status = ''
        if download_pdf:
            pdf_href = result.get('pdfHref', '')
            if pdf_href:
                filename = safe_filename(result['title'])
                save_path = os.path.join(PDF_DIR, filename)
                async with page.expect_download() as dl_info:
                    await page.goto(pdf_href)
                download = await dl_info.value
                await download.save_as(save_path)
                pdf_status = f'\nPDF 已儲存：{save_path}'
            else:
                pdf_status = '\nPDF：找不到下載連結（可能無訂閱）'

        await browser.close()
        return (
            f"標題：{result['title']}\n"
            f"作者：{result['authors']}\n"
            f"期刊：{result['journal']}\n\n"
            f"摘要：\n{result['abstract']}\n\n"
            f"關鍵字：{result['keywords']}"
            f"{pdf_status}"
        )


async def fetch_ieee(url: str, download_pdf: bool = False) -> str:
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            accept_downloads=True,
        )
        page = await ctx.new_page()
        await page.goto(url, wait_until='networkidle', timeout=30000)

        result = await page.evaluate("""() => {
            const title = document.querySelector('.document-title span')?.innerText || document.title;
            const abstract = document.querySelector('.abstract-text .u-mb-1')?.innerText
                           || document.querySelector('.abstract-text')?.innerText || '';
            const authors = Array.from(document.querySelectorAll('.authors-info span[id]'))
                           .map(a => a.innerText).join(', ');
            const pdfHref = document.querySelector('a.pdf-btn-icononly, a[href*="/stamp/stamp.jsp"], a[title*="PDF"]')?.href || '';
            return { title, abstract, authors, pdfHref };
        }""")

        pdf_status = ''
        if download_pdf:
            pdf_href = result.get('pdfHref', '')
            if pdf_href:
                filename = safe_filename(result['title'])
                save_path = os.path.join(PDF_DIR, filename)
                async with page.expect_download() as dl_info:
                    await page.goto(pdf_href)
                download = await dl_info.value
                await download.save_as(save_path)
                pdf_status = f'\nPDF 已儲存：{save_path}'
            else:
                pdf_status = '\nPDF：找不到下載連結（可能無訂閱）'

        await browser.close()
        return (
            f"標題：{result['title']}\n"
            f"作者：{result['authors']}\n\n"
            f"摘要：\n{result['abstract']}"
            f"{pdf_status}"
        )


async def main():
    if len(sys.argv) < 2:
        print("用法：python3 academic_fetch.py <URL> [--pdf]")
        sys.exit(1)

    url = sys.argv[1]
    download_pdf = '--pdf' in sys.argv

    if 'sciencedirect.com' in url:
        print(await fetch_sciencedirect(url, download_pdf))
    elif 'ieeexplore.ieee.org' in url:
        print(await fetch_ieee(url, download_pdf))
    else:
        print("僅支援 ScienceDirect 或 IEEE Xplore 網址")
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())
