from pdf2image import convert_from_path
import os

# 設定輸入和輸出資料夾
input_folder = "/app/input_pdfs"
output_folder = "/app/output_images"

# 設定解析度 (dpi) 來確保圖片清晰度
DPI = 600  # 解析度設定 (可調整 300, 600, 1200)

# 確保資料夾存在
os.makedirs(input_folder, exist_ok=True)
os.makedirs(output_folder, exist_ok=True)


def pdf_to_images(pdf_filename):
    pdf_path = os.path.join(input_folder, pdf_filename)

    if not os.path.exists(pdf_path):
        print(f"錯誤: 找不到 {pdf_filename}")
        return

    # 轉換 PDF 每頁為圖片
    images = convert_from_path(pdf_path, dpi=DPI)

    for i, img in enumerate(images):
        img_path = os.path.join(
            output_folder, f"{pdf_filename}_page_{i+1}.png")
        img.save(img_path, "PNG")  # 無損 PNG
        print(f"已儲存: {img_path}")


if __name__ == "__main__":
    pdf_files = [f for f in os.listdir(input_folder) if f.endswith(".pdf")]

    if not pdf_files:
        print("錯誤: input_pdfs 資料夾內沒有 PDF 檔案")
    else:
        for pdf in pdf_files:
            print(f"正在處理: {pdf}")
            pdf_to_images(pdf)

    print("所有 PDF 轉換完成！圖片存放於 output_images/")
