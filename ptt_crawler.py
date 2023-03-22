import requests
from datetime import datetime
from bs4 import BeautifulSoup
import re
import time
import datetime
import pandas as pd

post_owner_tag = "article-meta-value"

class Crawler:
    ptt_url = "https://www.ptt.cc"

    def __init__(self, board):
        self.board_url = f"/bbs/{board}"
        self.board = board
        self.contents = []

    def get_board_oddest_number(self, board_page_url):
        request = requests.get(board_page_url, cookies = {"over18": "1"})
        
        if request.status_code == 404:
            print("No such board")
            return
        print(board_page_url)
        page_text = request.text
        soup = BeautifulSoup(page_text, "lxml")
        oddest_boarb_url = soup.find("div", "btn-group btn-group-paging").find_all("a")[0].attrs["href"]
        match = re.search(r'page=(\d+)', oddest_boarb_url)
        if match:
            latest_page_number = int(match.group(1))
        return latest_page_number

    def get_post_content_with_keywords(self, post):
        post_url_index = post.find("div", "title").a.attrs["href"]
        print("post_url_index", post_url_index)
        if not post_url_index:
            return None
        post_time_str = post.find("div", "date").text.strip()
        post_time_obj = post_time_str
        post_url = Crawler.ptt_url + post_url_index
        time.sleep(1)
        post_request_result = requests.get(post_url, cookies = {"over18": "1"}).text
        article_soup = BeautifulSoup(post_request_result, "lxml")
        title = article_soup.find("title").text
        content = article_soup.find("meta", property="og:description").get("content")

        return post_url ,post_time_obj, title, content, article_soup

    def get_data(self, date=None, next_page=None, keyword=None, num_posts=None):
        if not next_page:
            next_page = self.board_url
        board_page_url = f"{Crawler.ptt_url}{next_page}/search?page=1&q={keyword}"
        print(board_page_url)
    
        board_oddest_number = self.get_board_oddest_number(board_page_url)
        df = pd.DataFrame(columns=['post_url', 'post_time', 'post_title', 'post_content', 'comment'])

        for board_page_index in range(1, board_oddest_number+1):
            board_page_url = f"{Crawler.ptt_url}{next_page}/search?page={board_page_index}&q={keyword}"

            request = requests.get(board_page_url, cookies={"over18": "1"})
            if request.status_code == 404:
                print("No such page")
                break

            page_text = request.text
            soup = BeautifulSoup(page_text, "lxml")

            for post in soup.select("div.r-ent"):
                title = None
                content = None
                result = self.get_post_content_with_keywords(post)
                if not result:
                    continue
                post_url, post_time_obj, title, content, article_soup = result

                if not title or not content:
                    continue

                for push in article_soup.find_all("span", class_="push-content"):
                    push = push.text[2:]
                    if len(push) <= 0:
                        continue
                    
                    
                    new_row = {'post_url': post_url,
                                'post_time': post_time_obj,
                                'post_title': title,
                                'post_content': content,
                                'comment': push}
                    new_df = pd.DataFrame(new_row, index=[0])
                    df = pd.concat([df, new_df], ignore_index=True) 
        return df
                
def main():
    board = "biker"
    crawler = Crawler(board)
    date = "2023-03-17"
    keywordlist = ["狗肉", "gogoro"]
    for keyword in keywordlist:
        keyword_ckeck_df = crawler.get_data(date = date, 
                                            next_page = None, 
                                            keyword = keyword,
                                            num_posts = None)
    print("keyword_ckeck_df.head(5)")
    print(keyword_ckeck_df.head(5))
    today_str = datetime.datetime.today().strftime("%m-%d-%Y-%H-%M-%S")
    filename = f'gogoro_post_push_result_{today_str}.csv'
    try:
        keyword_ckeck_df.to_csv(filename, index=False,encoding="utf_8_sig")
        print("csv export successfully")
    except Exception as e:
        print(str(e))

if __name__ == '__main__':
    main()