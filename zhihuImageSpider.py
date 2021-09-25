import time
import requests
import re
from bs4 import BeautifulSoup
from concurrent import futures

class Zhihu():
    headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36",
            'Accept-Encoding': 'gzip, deflate'
    }
    maxWorkders = 20
    cnt = 0

    def auto(self, qIDs):
        imgUrls = self.getImgUrls(qIDs)
        self.downloadConcurrent(imgUrls)

    def getImgUrls(self, qIDs):
        limit = 10  # 当页条数
        offset = 0  # 偏移量
        picReg = re.compile('<noscript>.*?data-original="(.*?)".*?</noscript>', re.S)   # 用于匹配回答内容中的图片
        picUrls = []
        for qID in qIDs:
            answer_url = f'https://www.zhihu.com/api/v4/questions/{qID}/answers'   # 知乎问题地址
            while True:
                # 请求参数
                data = {
                    'include': """data[*].is_normal,admin_closed_comment,reward_info,is_collapsed,annotation_action,annotation_detail,collapse_reason,is_sticky,collapsed_by,suggest_edit,comment_count,can_comment,content,editable_content,voteup_count,reshipment_settings,comment_permission,created_time,updated_time,review_info,relevant_info,question,excerpt,relationship.is_authorized,is_author,voting,is_thanked,is_nothelp,is_labeled,is_recognized,paid_info,paid_info_content;data[*].mark_infos[*].url;data[*].author.follower_count,badge[*].topics""",
                    'limit': limit,
                    'offset': offset,
                }
                response = requests.get(answer_url, params=data, headers=self.headers)
                resp = response.json()
                answers = resp.get('data')  # 当前页所有回答
                for answer in answers:
                    content = answer['content']
                    # 图片url
                    picUrls += re.findall(picReg, content)
                paging = resp.get('paging')
                # is_end  = True 已到最后一页
                if paging['is_end'] or len(picUrls) > 2000:
                    print('图片链接爬取完毕')
                    break
                offset += limit
                print(f'已获取前 {offset} 个回答，当前链接总数为 {len(picUrls)}')
        picUrls = [picUrl[:picUrl.rindex('?')] for picUrl in picUrls]
        picUrls = list(set(picUrls))
        return picUrls
    
    def downloadImage(self, imgUrls):
        cnt = 0
        for imgUrl in imgUrls:
            r = requests.get(imgUrl, headers=self.headers)
            print(imgUrl, r.status_code)
            if r.status_code == 200:
                bin = r.content
                fileName = imgUrl[imgUrl.rindex('/')+1:]
                with open("./data/" + fileName, 'wb') as file:
                    file.write(bin)
                    cnt += 1
        print(f"{cnt} images saved.")
    
    def downloadConcurrent(self, imgUrls):
        tasks = min(self.maxWorkders, len(imgUrls))
        with futures.ThreadPoolExecutor(tasks) as executor:
            res = executor.map(self.saveImg, imgUrls)
        return len(list(res))
    
    def saveImg(self, imgUrl):
        r = requests.get(imgUrl, headers=self.headers)
        if r.status_code == 200:
            bin = r.content
            fileName = imgUrl[imgUrl.rindex('/')+1:]
            with open("./data/" + fileName, 'wb') as file:
                file.write(bin)
            self.cnt += 1
            if self.cnt % 50 == 0:
                print(f"{self.cnt} images saved.")
        else:
            print(f"Download Fail. Status code: {r.status_code}")

if __name__ == "__main__":
    qIDs = ["319371540"]
    # qIDs = ["482559530"]
    start = time.time()
    spider = Zhihu()
    spider.auto(qIDs)
    print(f"Time cost {time.time()-start}")