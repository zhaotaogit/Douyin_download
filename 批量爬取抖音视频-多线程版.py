# -*- coding = utf-8 -*-
# @Time : 2021/6/19 23:57
# @File : 批量爬取抖音视频-多线程版.py
# @Software: PyCharm
# -*- coding = utf-8 -*-
# @Time : 2021/6/19 19:16
# @File : 批量爬取抖音视频.py
# @Software: PyCharm
import random
import traceback

import requests
import re
import os
from concurrent.futures import ThreadPoolExecutor
import time

start = time.time()

def generate_random_str(randomlength=16):
    """
    根据传入长度产生随机字符串
    """
    random_str = ''
    base_str = 'ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghigklmnopqrstuvwxyz0123456789='
    length = len(base_str) - 1
    for _ in range(randomlength):
        random_str += base_str[random.randint(0, length)]
    return random_str


headers = {
    'authority': 'www.douyin.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-language': 'zh-CN,zh;q=0.9',
    'cache-control': 'max-age=0',
    'sec-ch-ua': '"Google Chrome";v="108", "Chromium";v="108", "Not=A?Brand";v="8"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Mobile Safari/537.36 Edg/87.0.664.66',
    'Cookie': 'msToken=%s' % generate_random_str(107)
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
    number_of_works = 'https://www.iesdouyin.com/aweme/v1/web/aweme/post/?sec_user_id=' + sec_uid +'&count=35&max_cursor=0&aid=1128&version_name=23.5.0&device_platform=android&os_version=2333'
    resp1 = requests.get(number_of_works, headers=headers)
    nickname = resp1.json()['aweme_list'][0]['author']['nickname']
    return nickname


# 创建存放视频的文件夹
def mkdir(nickname):
    path = os.path.join(os.getcwd(), nickname)
    if not os.path.exists(path):
        os.mkdir(path)
    os.chdir(path)
    print(f'已成功创建文件夹{path},将用于保存视频!')


# 获取作者视频并保存到本地
def download_video_url(sec_uid):
    max_cursor = 0
    n = 1
    rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
    while True:
        # 获取作者作品名和作品链接
        # requ_url = 'https://www.iesdouyin.com/web/api/v2/aweme/post/?sec_uid=' + sec_uid + f'&count=21&max_cursor={max_cursor}&aid=1128&_signature=RmgLIQAAJqehH.Mn4SqZZEZoCz&dytk='
        requ_url = 'https://www.iesdouyin.com/aweme/v1/web/aweme/post/?sec_user_id=' + sec_uid +f'&count=35&max_cursor={max_cursor}&aid=1128&version_name=23.5.0&device_platform=android&os_version=2333'
        resp2 = requests.get(requ_url, headers=headers)
        print(resp2.url)
        print(resp2.status_code)
        # 遍历出视频链接和视频标题
        for i in resp2.json()['aweme_list']:
            # 获取标题
            name = re.sub(rstr, '_', i['desc']) + '.mp4'  # 替换掉不能当做文件名的字符
            name = f'{n}.' + name
            if i.get('video'):
                # 获取链接
                if i.get('video').get('download_addr'):
                    href = i['video']['download_addr']['url_list'][0]
                elif i.get('video').get('bit_rate'):
                    href = i['video']['bit_rate']['play_addr']['url_list'][0]
                # 将标题和链接添加到列表
                video_name_list.append(name)
                video_urls_list.append(href)
            elif i.get('images'):
                images_lst = i.get('images')
                for j in range(len(images_lst)):
                    images_name_list.append(name+f'_({j})')
                    images_urls_list.append(images_lst[j].get('download_url_list')[0])
            n += 1
            print(name, '----------获取下载链接成功')
        if resp2.json()['has_more'] == 0:
            print(images_urls_list)
            return
        max_cursor = resp2.json()['max_cursor']


def download_write_video(name, url):
    with open(name, 'wb') as f:
        f.write(requests.get(url, headers=headers).content)
        print(name, '-------下载完成')


video_urls_list = []
video_name_list = []
images_name_list = []
images_urls_list = []

def main():
    # 用户输入作者主页链接
    print('本程序仅用于批量爬取抖音作者的所有视频!若程序出现问题，请联系作者:QQ1787417712')
    author_url = input('请输入作者的主页链接:')
    # UA代理
    sec_uid = get_sec_uid(author_url)
    nickname = get_nickname_count(sec_uid)
    mkdir(nickname)
    print('开始获取作者所有视频的下载链接')
    download_video_url( sec_uid)
    print('全部链接获取完毕,开始下载视频')



if __name__ == '__main__':
    main()
    with ThreadPoolExecutor(30) as t:
        for i in range(len(video_urls_list)):
            t.submit(download_write_video,name=video_name_list[i], url=video_urls_list[i])
    print('全部下载完成!')
    end = time.time()
    print(end-start)