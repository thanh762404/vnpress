import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import time
import schedule


def extract_article_info(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        meta_desc = soup.find('meta', attrs={'name': 'description'})
        summary = meta_desc['content'] if meta_desc else ''

        meta_img = soup.find('meta', property='og:image')
        image = meta_img['content'] if meta_img else ''

        article_body = soup.find('article')
        paragraphs = article_body.find_all('p') if article_body else []
        full_text = '\n'.join(p.get_text(strip=True) for p in paragraphs)

        return summary, image, full_text
    except Exception as err:
        print(f"⚠️ Lỗi khi xử lý {url}: {err}")
        return '', '', ''


def crawl_vnexpress_entertainment(max_pages=3):
    base_link = "https://vnexpress.net/giai-tri"
    collected_articles = []

    for page in range(1, max_pages + 1):
        page_url = base_link if page == 1 else f"{base_link}-p{page}"
        print(f"🔎 Đang thu thập: {page_url}")

        response = requests.get(page_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        news_items = soup.select("article.item-news")

        for item in news_items:
            anchor = item.find('a', href=True)
            headline_tag = item.find('h3') or item.find('h2')

            if anchor and headline_tag:
                news_url = anchor['href']
                headline = headline_tag.get_text(strip=True)

                summary, image_url, content = extract_article_info(news_url)

                collected_articles.append({
                    'Tiêu đề': headline,
                    'Mô tả': summary,
                    'Hình ảnh': image_url,
                    'Nội dung': content,
                    'Link': news_url
                })

        time.sleep(2)  # tránh bị chặn

    df = pd.DataFrame(collected_articles)
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    filename = f"vnexpress_entertainment_{today_str}.csv"
    df.to_csv(filename, index=False, encoding='utf-8-sig')
    print(f"✅ Đã lưu dữ liệu vào {filename}")


if __name__ == "__main__":
    # Thử nghiệm ngay
    # crawl_vnexpress_entertainment()

    # Lên lịch chạy hằng ngày lúc 06:00
    schedule.every().day.at("06:00").do(crawl_vnexpress_entertainment)

    print("🕕 Đang đợi đến 06:00 để tự động thu thập...")

    while True:
        schedule.run_pending()
        time.sleep(60)
