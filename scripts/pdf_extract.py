#!/usr/bin/env python3
"""
從 PDF 提取全文與圖片
用法：python3 pdf_extract.py <pdf_path> [--images-dir <dir>]
回傳：full_text (str)，圖片存至 images_dir/
"""
import sys
import os
import json
import fitz  # PyMuPDF


def extract(pdf_path: str, images_dir=None) -> dict:
    doc = fitz.open(pdf_path)

    if images_dir:
        os.makedirs(images_dir, exist_ok=True)

    full_text = []
    saved_images = []

    for page_num, page in enumerate(doc, start=1):
        text = page.get_text("text").strip()
        if text:
            full_text.append(f"[Page {page_num}]\n{text}")

        if images_dir:
            for img_index, img in enumerate(page.get_images(full=True)):
                xref = img[0]
                base_image = doc.extract_image(xref)
                ext = base_image["ext"]
                # 跳過太小的圖（通常是圖示或雜訊）
                if base_image["width"] < 100 or base_image["height"] < 100:
                    continue
                filename = f"p{page_num:02d}_img{img_index:02d}.{ext}"
                save_path = os.path.join(images_dir, filename)
                with open(save_path, "wb") as f:
                    f.write(base_image["image"])
                saved_images.append({
                    "path": save_path,
                    "page": page_num,
                    "width": base_image["width"],
                    "height": base_image["height"],
                })

    doc.close()
    return {
        "text": "\n\n".join(full_text),
        "images": saved_images,
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法：python3 pdf_extract.py <pdf_path> [--images-dir <dir>]")
        sys.exit(1)

    pdf_path = sys.argv[1]
    images_dir = None
    if "--images-dir" in sys.argv:
        idx = sys.argv.index("--images-dir")
        images_dir = sys.argv[idx + 1]

    result = extract(pdf_path, images_dir)
    print(f"全文字數：{len(result['text'])} 字元")
    print(f"提取圖片：{len(result['images'])} 張")
    if result["images"]:
        for img in result["images"]:
            print(f"  [{img['page']}頁] {img['path']} ({img['width']}×{img['height']})")
