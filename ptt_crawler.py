import requests
from datetime import datetime
from bs4 import BeautifulSoup
import re

post_owner_tag = "article-meta-value"


class Crawler:
    ptt_url = "https://www.ptt.cc"

    def __init__(self, board):
        self.board_url = f"/bbs/{board}"
        self.board = board
        self.contents = []
    
    def get_board_page_url(self, page_text):
        soup = BeautifulSoup(page_text, "lxml")
        next_page_url = soup.find("div", "btn-group btn-group-paging").find_all("a")[1].attrs["href"] 

        match = re.search(r"\d+", next_page_url)
        if match:
            latest_page_number = int(match.group())+ 1
        
        page_url = f"{Crawler.ptt_url+self.board_url}index{latest_page_number}.html"
        return page_url
        
    def get_data(self, date=None, next_page=None, keyword=None, num_posts=100):
        if not next_page:
            next_page = self.board_url
        
        request = requests.get(Crawler.ptt_url + next_page, cookies = {"over18": "1"})
        if request.status_code == 404:
            print("No such board")
            return
        
        page_text = request.text
        page_url = self.get_board_page_url(page_text)
        print(page_url)

        if not date:
            date = datetime(2023, 3, 19) 

        page_text = page_text.split("r-list-sep")[0]
        soup = BeautifulSoup(page_text, "lxml")

        for post in soup.select("div.r-ent"):
            post_url_index = post.find("div", "title").a.attrs["href"]
            if not post_url_index:
                continue

            post_request_result = requests.get(Crawler.ptt_url + post_url_index, cookies = {"over18": "1"}).text
            post_url = Crawler.ptt_url + post_url_index
            print(post_url)
            article_soup = BeautifulSoup(post_request_result, "lxml")
            title = article_soup.find("title").text
            content = article_soup.find("meta", property="og:description").get("content")

            if not title or not content:
                continue
            
            if keyword and keyword not in title and keyword not in content:
                continue   
            self.contents.append(f"{title}:{content}")

            push_list = []
            for push in article_soup.find_all("span", class_="push-content"):
                push = push.text[2:]
                if len(push) <= 0:
                    continue
                push_list.append(push)
            self.contents.append(push_list)
            time_str = post.find("div", "date").text.strip()
            time_obj = datetime.strptime(time_str+"/2020", '%m/%d/%Y')
            if time_obj < date:  # 不是今天的文章
                return
            else:
                if len(self.contents)/2 > num_posts:
                    return
            
def main():
    board = "biker"
    crawler = Crawler(board)
    keywords_list = ["狗肉", "gogoro"] 
    for keyword in keywords_list:
        print(keyword)
        crawler.get_data(date = datetime(2023, 3, 16), 
                        keyword=keyword, 
                        num_posts=10)
    content_list = crawler.contents
    if len(content_list) == 0:
        print(f"no any key word in this page")
    else:
        print(f"get_data successfully\n{content_list}")

if __name__ == '__main__':
    main()