# -*- coding = utf-8 -*-
# @Time : 2021/6/20 0:00
# @File : 批量爬取抖音视频-函数版.py
# @Software: PyCharm
import requests
import re
import os
import time

start = time.time()

headers = {
    'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Mobile Safari/537.36'
}


# 获取sec_udi
def get_sec_uid(author_url):
    # 访问作者主页链接
    resp = requests.get(author_url, headers=headers)
    # 获取重定向后的作者主页链接
    author_url = resp.url
    # 根据作者主页链接拿到sec_uid
    sec_uid = author_url.split('sec_uid=')[1].split('&')[0]
    resp.close()
    return sec_uid


# 获取作者作品总数和作者名称
def get_nickname_count(sec_uid):
    number_of_works = 'https://www.iesdouyin.com/web/api/v2/user/info/?sec_uid=' + sec_uid
    resp1 = requests.get(number_of_works, headers=headers)
    wokrs_count = resp1.json()['user_info']['aweme_count']
    nickname = resp1.json()['user_info']['nickname']
    return nickname, wokrs_count


# 创建存放视频的文件夹
def mkdir(nickname):
    path = os.path.join(os.getcwd(), nickname)
    if not os.path.exists(path):
        os.mkdir(path)
    os.chdir(path)
    print(f'已成功创建文件夹{path},将用于保存视频!')


# 获取作者视频并保存到本地
def download_video_url(wokrs_count, sec_uid):
    max_cursor = 0
    n = 1
    rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
    for x in range(wokrs_count // 20):
        # 获取作者作品名和作品链接
        requ_url = 'https://www.iesdouyin.com/web/api/v2/aweme/post/?sec_uid=' + sec_uid + f'&count=21&max_cursor={max_cursor}&aid=1128&_signature=RmgLIQAAJqehH.Mn4SqZZEZoCz&dytk='
        resp2 = requests.get(requ_url, headers=headers)
        # 遍历出视频链接和视频标题
        for i in resp2.json()['aweme_list']:
            # 获取标题
            name = re.sub(rstr, '_', i['desc']) + '.mp4'  # 替换掉不能当做文件名的字符
            name = f'{n}.' + name
            # 获取链接
            href = i['video']['play_addr_lowbr']['url_list'][0]
            # 将标题和链接添加到列表
            video_name_list.append(name)
            video_urls_list.append(href)
            n += 1
            print(name, '----------获取下载链接成功')
        max_cursor = resp2.json()['max_cursor']


def download_write_video(name, url):
    with open(name, 'wb') as f:
        f.write(requests.get(url, headers=headers).content)
        print(name, '-------下载完成')


video_urls_list = []
video_name_list = []


def main():
    # 用户输入作者主页链接
    print('本程序仅用于批量爬取抖音作者的所有视频!若程序出现问题，请联系作者:QQ1787417712')
    author_url = input('请输入作者的主页链接:')
    # UA代理
    sec_uid = get_sec_uid(author_url)
    nickname, works_count = get_nickname_count(sec_uid)
    mkdir(nickname)
    print('开始获取作者所有视频的下载链接')
    download_video_url(works_count, sec_uid)
    print('全部链接获取完毕,开始下载视频')
    for i in range(len(video_urls_list)):
        download_write_video(video_name_list[i], video_urls_list[i])
    print('全部下载完成!')


if __name__ == '__main__':
    main()
    end = time.time()
    print(end-start)
