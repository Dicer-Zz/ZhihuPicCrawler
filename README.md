# 知乎回答图片爬虫

这是一个知乎回答的图片脚本，代码不长，但是：

1. 免登录不用账号密码
2. 高并发加快下载速度
3. 支持同时爬取多个问题

当然，也存在一些亟待解决的问题，header没有池化，因此在长时间运行之后可能会出现403，不过一般下载量在数个G之内问题都不大。如果真出现403，那么更换一下header即可。

欢迎提出issue & PR

# Usage

通过知乎问题链接可以获取qID（问题ID）比如 https://www.zhihu.com/question/488737569 其中 488737569 就是这个问题的唯一ID。
然后更改`__main__`中的qIDs。

然后执行：

``` shell
python Spider.py
```

# Reference
https://github.com/python3xxx/zhihu_spider/blob/master/zhihu_spider.py
