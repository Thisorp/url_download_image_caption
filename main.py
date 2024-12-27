import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import argparse

# Tạo thư mục lưu ảnh
def create_directory(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

# Tải ảnh và lưu vào thư mục
def download_image(image_url, folder_path, image_name):
    response = requests.get(image_url, stream=True)
    if response.status_code == 200:
        image_path = os.path.join(folder_path, image_name)
        with open(image_path, 'wb') as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        print(f"Downloaded: {image_path}")
    else:
        print(f"Failed to download image: {image_url}")

# Lấy ảnh và caption từ trang web
def scrape_images_and_captions(url, folder_path):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    create_directory(folder_path)

    # Tìm tất cả các thẻ <img> và caption liên quan
    images = soup.find_all('img')
    for index, img in enumerate(images):
        img_url = img.get('src')
        if not img_url or img_url.startswith("data:image"):  # Bỏ qua data:image
            continue
        img_url = urljoin(url, img_url)  # Xử lý link tương đối thành link tuyệt đối
        caption = img.get('alt', f"Image_{index}")  # Lấy thuộc tính alt làm caption
        image_name = f"{caption.replace(' ', '_')}.jpg"
        download_image(img_url, folder_path, image_name)


# Hàm chính
def main():
    parser = argparse.ArgumentParser(description="Scrape images and captions from a webpage.")
    parser.add_argument('--link', type=str, required=True, help="URL of the webpage to scrape")
    parser.add_argument('--folder', type=str, default="images", help="Folder name to save images (relative to script location)")
    args = parser.parse_args()

    # Đường dẫn tuyệt đối tới thư mục lưu ảnh
    script_dir = os.path.dirname(os.path.abspath(__file__))
    folder_path = os.path.join(script_dir, args.folder)

    scrape_images_and_captions(args.link, folder_path)

if __name__ == "__main__":
    main()
