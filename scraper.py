import os
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

def create_images_folder(folder_name='images'):
    """Tạo thư mục để lưu hình ảnh nếu chưa tồn tại."""
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    return folder_name

def is_valid_url(url):
    """Kiểm tra xem URL có hợp lệ không."""
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

def get_page_content(url):
    """Lấy nội dung HTML của trang web."""
    try:
        response = requests.get(url)
        response.raise_for_status()  # Kiểm tra lỗi HTTP
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def get_all_images(soup, base_url):
    """Lấy tất cả các thẻ img từ trang và trả về danh sách các URL hình ảnh."""
    img_tags = soup.find_all('img')
    urls = []
    for img in img_tags:
        img_url = img.get('src')
        if not img_url:
            # Thẻ img không có src
            continue
        # Xử lý các URL tương đối
        img_url = urljoin(base_url, img_url)
        # Kiểm tra tính hợp lệ của URL
        if is_valid_url(img_url):
            urls.append(img_url)
    return urls

def get_caption(img_tag):
    """Lấy caption cho hình ảnh từ thẻ img."""
    # Cách đơn giản nhất là kiểm tra thẻ alt
    caption = img_tag.get('alt')
    if caption:
        return caption.strip()
    # Nếu không có alt, có thể kiểm tra thẻ cha
    parent = img_tag.find_parent()
    if parent:
        # Tìm thẻ <figcaption> nếu có
        figcaption = parent.find('figcaption')
        if figcaption:
            return figcaption.get_text().strip()
    return "No caption"

def download_image(img_url, folder):
    """Tải xuống hình ảnh và lưu vào thư mục."""
    try:
        response = requests.get(img_url, stream=True)
        response.raise_for_status()
        # Lấy tên file từ URL
        filename = os.path.basename(urlparse(img_url).path)
        if not filename:
            filename = "image.jpg"
        file_path = os.path.join(folder, filename)
        # Nếu file đã tồn tại, thêm số để tránh ghi đè
        base, extension = os.path.splitext(file_path)
        counter = 1
        while os.path.exists(file_path):
            file_path = f"{base}_{counter}{extension}"
            counter += 1
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        return file_path
    except requests.RequestException as e:
        print(f"Error downloading {img_url}: {e}")
        return None

def save_caption(file_path, caption):
    """Lưu caption vào file text cùng với hình ảnh."""
    caption_file = f"{file_path}.txt"
    with open(caption_file, 'w', encoding='utf-8') as f:
        f.write(caption)

def scrape_images(url, folder='images'):
    """Chức năng chính để scrape hình ảnh và caption từ trang web."""
    if not is_valid_url(url):
        print("URL không hợp lệ.")
        return

    content = get_page_content(url)
    if not content:
        print("Không thể lấy nội dung trang.")
        return

    soup = BeautifulSoup(content, 'html.parser')
    images = get_all_images(soup, url)
    print(f"Tìm thấy {len(images)} hình ảnh.")

    for img_url in images:
        print(f"Đang tải xuống: {img_url}")
        file_path = download_image(img_url, folder)
        if file_path:
            # Tìm thẻ img tương ứng để lấy caption
            img_tag = soup.find('img', src=img_url.replace(url, ''))
            caption = get_caption(img_tag) if img_tag else "No caption"
            save_caption(file_path, caption)
            print(f"Lưu hình ảnh và caption vào: {file_path}")
        else:
            print(f"Không thể tải xuống hình ảnh: {img_url}")

def main():
    url = input("Nhập URL của trang web: ").strip()
    images_folder = create_images_folder()
    scrape_images(url, images_folder)
    print("Hoàn thành.")

if __name__ == "__main__":
    main()
