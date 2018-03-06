# -*- coding: utf-8 -*-
import json

import scrapy
from scrapy import Request

from movie.items import PostItem, CommentItem, ComposerItem, CopyrightItem

# comment_api = "http://www.xinpianchang.com/article/filmplay/ts-getCommentApi?id=%s&ajax=1&page=%s"
# http://www.xinpianchang.com/article/filmplay/ts-getCommentApi/id-10177348/page-1
comment_api = "http://www.xinpianchang.com/article/filmplay/ts-getCommentApi/id-%s/page-1"
vip_map = {
    "yellow-v": 1,
    "blue-v": 2,
}

def conver_int(s):
    return int(s.replace(",","")) if s else 0

class DiscoverySpider(scrapy.Spider):
    name = 'discovery'
    allowed_domains = ['www.xinpianchang.com']
    start_urls = ['http://www.xinpianchang.com/channel/index/id-0/sort-like']
    root_urls = "http://www.xinpianchang.com"

    def parse(self, response):
        post_url = "http://www.xinpianchang.com/a%s?from=ArticleList"
        post_list = response.xpath("//ul[@class='video-list']/li")

        for post in post_list:
            post_id = post.xpath("./@data-articleid").get()
            post_title = post.xpath("./div[@class='video-con']/a/p/text()").get()
            thumbnail = post.xpath("./a/img/@_src").get()
            # print(post_title, post_id)
            request = Request(post_url % post_id, callback=self.parse_post)
            request.meta["pid"] = post_id
            request.meta["thumbnail"] = thumbnail
            request.meta["title"] = post_title
            yield request

            next_page = response.xpath("//div[@class='page']/a[last()]/@href").get()
            print(next_page)
            if next_page:
                yield response.follow(next_page, callback=self.parse)

    def parse_post(self, response):
        post = PostItem()
        post["pid"] = response.meta["pid"]
        post["thumbnail"] = response.meta["thumbnail"]
        # post["title"]=response.xpath().get()
        post["title"] = response.meta["title"]
        post["preview"] = response.xpath('//div[@class="filmplay"]//img/@src').get()
        post["video"] = response.xpath('//video[@id="xpc_video"]/@src').get()
        # post["video_format"]=response.xpath().get()
        post["video_format"] = ""
        post["category"] = response.xpath('//span[@class="cate v-center"]/text()').get()
        post['created_at'] = response.xpath('//span[contains(@class,"update-time")]/i/text()').get()
        post["play_counts"] = conver_int(response.xpath('//i[contains(@class,"play-counts")]/@data-curplaycounts').get())
        post["like_counts"] = conver_int(response.xpath('//span[contains(@class,"like-counts")]/@data-counts').get())
        post["description"] = response.xpath('//p[contains(@class,"desc")]/text()').get()
        yield post

        creator_list = response.xpath('//div[contains(@class,"filmplay-creator")]/ul[@class="creator-list"]/li')
        for creator in creator_list:
            user_page = creator.xpath('./a/@href').get()
            user_id = creator.xpath('./a/@data-userid').get()
            request = Request("%s%s" % (self.root_urls, user_page), callback=self.parse_composer)
            request.meta["cid"] = user_id
            yield request

            cr = CopyrightItem()
            cr["pid"] = response.meta["pid"]
            cr["cid"] = user_id
            cr["pcid"] = "%s_%s" % (cr["pid"], cr["cid"])
            cr["roles"] = creator.xpath('.//span[contains(@class,"roles")]/text()').get()
            yield cr

        # http://www.xinpianchang.com/article/filmplay/ts-getCommentApi?id=81999&ajax=1&page=1
        request = Request(comment_api % post["pid"], callback=self.parse_comment)
        request.meta["pid"] = post["pid"]
        # request.meta["cur_page"] = 1
        yield request

    def parse_comment(self, response):
        if response.text:
            pid = response.meta["pid"]
            result = json.loads(response.text)
            # print(result)

            next_page = result["data"]["next_page_url"]
            if next_page:
                request = Request(next_page, callback=self.parse_comment)
                request.meta["pid"] = pid
                yield request

            comments = result["data"]["list"]
            for c in comments:
                comment = CommentItem()
                comment["commentid"] = int(c["commentid"])
                comment["pid"] = pid
                comment["cid"] = c["userInfo"]["userid"]
                comment["uname"] = c["userInfo"]["username"]
                comment["created_at"] = int(c["addtime_int"])
                comment["content"] = c["content"]
                comment["like_counts"] = conver_int(c["count_approve"])
                comment["avatar"]=c["userInfo"]["face"]
                if c["reply"]:
                    comment["reply"] = c["reply"] or 0
                yield comment

                request = Request("%s/u%s" % (self.root_urls, comment["cid"]), callback=self.parse_composer)
                request.meta["cid"] = comment["cid"]
                yield request


    def parse_composer(self, response):
        composer = ComposerItem()
        composer["cid"] = response.meta["cid"]
        composer["banner"] = response.xpath('//div[@class="banner-wrap"]/@style').get()
        if composer["banner"]:
            # 提取样式的链接
            composer["banner"] = composer["banner"].split("(")[-1][:-1]
        avatar_elem = response.xpath('//span[@class="avator-wrap-s"]')
        composer["avatar"] = avatar_elem.xpath('./img/@src').get()

        auth_style = avatar_elem.xpath('./span/@class').get()
        if auth_style:
            composer["verified"] = vip_map.get(auth_style.split(" ")[-1])

        composer["like_counts"] = conver_int(response.xpath('//span[contains(@class,"like-counts")]/text()').get())
        composer["fans_counts"] = conver_int(response.xpath('//span[contains(@class,"fans-counts")]/@data-counts').get())
        composer["follow_counts"] = conver_int(response.xpath('//span[@class="follow-wrap"]/span[last()]/text()').get())
        composer["name"] = response.xpath('//p[contains(@class, "creator-name")]/text()').get()
        composer["intro"] = response.xpath('//p[contains(@class, "creator-desc")]/text()').get()
        yield composer
