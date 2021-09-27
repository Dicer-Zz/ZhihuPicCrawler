import time
import requests
import re
import os
import argparse
from concurrent import futures


class Zhihu():
    """
    Class of ZhihuImgSpider.
    """

    def __init__(self, qIDs, numPics, maxSize, minSize, numWorkers):
        """initialization

        Parameters
        ----------
        qIDs : sequence of strings
            Ids of question.
        numPics : int
            Maximum number of picture crawled.
        maxSize : int
            Maximum size of picture.
        minSize : int
            Minimum size of picture.
        numWorkers : int
            Number of threads.
        """
        self.qIDs = qIDs
        self.numPics = numPics
        self.maxSize = maxSize
        self.minSize = minSize
        self.numWorkers = numWorkers
        self.imgCounter = 0
        self.imgSize = 0
        self.headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36",
            'Accept-Encoding': 'gzip, deflate'
        }

    def auto(self):
        """Automatic download
        """
        startTime = time.time()
        imgUrls = self.getImgUrls()
        self.downloadConcurrent(imgUrls)
        metric = "MB" if self.imgSize > 1024 else "KB"
        size = self.imgSize//1024 if self.imgSize > 1024 else self.imgSize
        costTime = time.time() - startTime
        print(
            f"{self.imgCounter} images downloaded. Image size: {size} {metric}.")
        print(
            f"Time cost: {costTime:.3f}s. {size/costTime:.3f} {metric}/s.")

    def getImgUrls(self):
        
        picReg = re.compile(
            '<noscript>.*?data-original="(.*?)".*?</noscript>', re.S)   # 用于匹配回答内容中的图片
        picUrls = []
        for qID in self.qIDs:
            limit = 10  # 当页条数
            offset = 0  # 偏移量
            # 知乎问题地址
            answer_url = f'https://www.zhihu.com/api/v4/questions/{qID}/answers'
            while True:
                # 请求参数
                data = {
                    'include': """data[*].is_normal,admin_closed_comment,reward_info,is_collapsed,annotation_action,annotation_detail,collapse_reason,is_sticky,collapsed_by,suggest_edit,comment_count,can_comment,content,editable_content,voteup_count,reshipment_settings,comment_permission,created_time,updated_time,review_info,relevant_info,question,excerpt,relationship.is_authorized,is_author,voting,is_thanked,is_nothelp,is_labeled,is_recognized,paid_info,paid_info_content;data[*].mark_infos[*].url;data[*].author.follower_count,badge[*].topics""",
                    'limit': limit,
                    'offset': offset,
                }
                response = requests.get(
                    answer_url, params=data, headers=self.headers)
                resp = response.json()
                answers = resp.get('data')  # 当前页所有回答
                for answer in answers:
                    content = answer['content']
                    # 图片url
                    picUrls += re.findall(picReg, content)
                paging = resp.get('paging')
                # is_end  = True 已到最后一页
                if paging['is_end'] or len(picUrls) > self.numPics*3:
                    print('图片链接爬取完毕')
                    break
                offset += limit
                print(f'已获取前 {offset} 个回答，当前链接总数为 {len(picUrls)}')
        picUrls = [picUrl[:picUrl.rindex('?')] for picUrl in picUrls]
        picUrls = list(set(picUrls))
        return picUrls

    def downloadConcurrent(self, imgUrls):
        """Download pictures concurrently.

        Parameters
        ----------
        imgUrls : sequence of strings
            Urls of images.

        Returns
        -------
        int
            Number of results.
        """
        if not os.path.isdir("./data"):
            os.mkdir("./data")
        tasks = min(self.numWorkers, len(imgUrls))
        with futures.ThreadPoolExecutor(tasks) as executor:
            res = executor.map(self.saveImg, imgUrls, timeout=5)
        return len(list(res))

    def saveImg(self, imgUrl):
        """Download one image from url

        Parameters
        ----------
        imgUrl : string
            Url of one image.
        """
        if self.imgCounter > self.numPics:  # Maybe wrong due to concurrent.
            return
        r = requests.get(imgUrl, headers=self.headers)
        if r.status_code == 200:
            length = r.headers["Content-Length"]
            if not self.minSize < int(length)//1024 < self.maxSize:
                return
            bin = r.content
            fileName = imgUrl[imgUrl.rindex('/')+1:]
            with open("./data/" + fileName, 'wb') as file:
                file.write(bin)
            self.imgCounter += 1
            self.imgSize += int(length)//1024
            if self.imgCounter % 50 == 0:
                metric = "MB" if self.imgSize > 1024 else "KB"
                size = self.imgSize//1024 if self.imgSize > 1024 else self.imgSize
                print(f"{self.imgCounter} images saved ({size} {metric}).")
        else:
            print(f"Download Fail. Status code: {r.status_code}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(
        description="This is a script that can download images from Zhihu.")
    ap.add_argument("-q", "--qIDs", nargs="+", required=True, default=[])
    ap.add_argument("--num_pic",
                    metavar="The number of pictures (Default: 2000)", type=int, default=2000)
    ap.add_argument(
        "--max_size", metavar="The maximum size(KB) limitation of pictures (Default: 10000)", type=int, default=10000)
    ap.add_argument(
        "--min_size", metavar="The minimum size(KB) limitation of pictures (Default: 200)", type=int, default=200)
    ap.add_argument(
        "--num_workers", metavar="The number of workers (Default: 20)", type=int, default=20)
    args = ap.parse_args()

    spider = Zhihu(args.qIDs, args.num_pic, args.max_size,
                   args.min_size, args.num_workers)
    spider.auto()
