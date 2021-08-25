# -*- coding = utf-8 -*-
# @Time : 2021/6/19 19:16
# @File : 批量爬取抖音视频.py
# @Software: PyCharm
import requests
import re
import os
import time
from lxml import etree
import sys
from concurrent.futures import ThreadPoolExecutor

headers = {
    'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Mobile Safari/537.36'
}
start = time.time()
path = os.getcwd()
rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'


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
    nickname = re.sub(rstr, '_', nickname)
    path = os.path.join(os.getcwd(), nickname)
    if not os.path.exists(path):
        os.mkdir(path)
    os.chdir(path)
    print(f'已成功创建文件夹{path},将用于保存视频!')


# 获取作者视频并保存到本地
def download_video_url(works_count, sec_uid):
    max_cursor = 0
    n = 0
    while True:
        # 获取作者作品名和作品链接
        requ_url = 'https://www.iesdouyin.com/web/api/v2/aweme/post/?sec_uid=' + sec_uid + f'&count=21&max_cursor={max_cursor}&aid=1128&_signature=RmgLIQAAJqehH.Mn4SqZZEZoCz&dytk='
        resp2 = requests.get(requ_url, headers=headers)
        # 遍历出视频链接和视频标题
        try:
            resp2.json()['aweme_list']
        except Exception as e:
            break
        for i in resp2.json()['aweme_list']:
            # 获取标题
            name = re.sub(rstr, '_', i['desc'])  # 替换掉不能当做文件名的字符
            name = re.sub(r'(#|@).*? ', '', name).split('@')[0].split('#')[0].replace('#', '').replace('@', '').strip()
            if name:
                name = name + '.mp4'
            else:
                name = str(int(round(time.time() * 100000, 0))) + '.mp4'
                time.sleep(0.01)
            # name = name + '.mp4' if name else str(int(round(time.time() * 100000, 0))) + '.mp4'
            # name = name + '.mp4'
            name = name.replace('你要去掉的字符', '想要替换成的字符')
            # 获取链接
            try:
                href = i['video']['play_addr']['url_list'][0]
            except Exception as e:
                continue
            # 将标题和链接添加到列表
            video_name_list.append(name)
            video_urls_list.append(href)
            print(name, '----------获取下载链接成功')
            n += 1
            if len(video_name_list) == works_count - len(already_video_name_list):
                print(f'获取到{n}个作者新视频，即将下载······')
                return
        min_cursor = resp2.json()['max_cursor']
        # if not min_cursor:
        #     print(f'获取到{n}个作者新视频，即将下载······')
        #     break
        max_cursor = min_cursor


# def download_write_video(name, url, timeout, num):
def download_write_video(name, url, num):
    try:
        name = num + ' - ' + name
        with open(name, 'wb') as f:
            f.write(requests.get(url, headers=headers).content)
    except Exception as e:
        download_failed_list.append(name + ':' + url)
        print(name + '因为网络原因下载失败,已跳过！')
        os.remove(name)
        print(e)


video_urls_list = []
video_name_list = []
already_video_name_list = []
download_failed_list = []


def count(x):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36'
        }
        resp = requests.get(url=x, headers=headers)
        html = etree.HTML(resp.text)
        works_count = html.xpath('//*[@id="root"]/div/div[2]/div/div[4]/div[1]/div[1]/div[1]/span/text()')[0]
        li_list_count = html.xpath('/html/body/div/div/div[2]/div/div[4]/div[1]/div[2]/ul/li[1]/a/@href')
        return int(works_count), li_list_count
    except Exception as e:
        print('因为网络问题发生错误，请重新尝试下载!')
        print(e)
        sys.exit()


def main():
    # 用户输入作者主页链接
    print('本程序仅用于批量爬取抖音作者的所有视频!若程序出现问题,请联系作者:QQ1787417712')
    # timeout = int(input('请输入下载卡住的等待时间:'))
    author_url = input('请输入作者的主页链接(多个作者链接用","英文的逗号分隔):')
    return author_url


if __name__ == '__main__':
    author_url = main()
    for x in author_url.split(','):
        os.chdir(path)
        sec_uid = get_sec_uid(x)
        nickname, works_count = get_nickname_count(sec_uid)
        mkdir(nickname)
        works_count,li_list_count = count(x)
        if works_count and li_list_count:
            for root, dirs, files in os.walk(os.getcwd()):
                for i in files:
                    already_video_name_list.append(i)
            if len(already_video_name_list) >= works_count:
                print('作者没有更新视频！')
            else:
                al_num = len(already_video_name_list)
                print(f'开始获取不存在本地的"{nickname}"视频的下载链接')
                download_video_url(works_count, sec_uid)
                print(f'"{nickname}"链接获取完毕,开始下载视频')
                with ThreadPoolExecutor(30) as t:
                    for i in range(len(video_urls_list) - 1, -1, -1):
                        num = al_num + len(video_urls_list) - i
                        # t.submit(download_write_video, name=video_name_list[i], url=video_urls_list[i], timeout=timeout,
                        #          num=str(num))
                        t.submit(download_write_video, name=video_name_list[i], url=video_urls_list[i],
                                 num=str(num))
                        print(
                            f'正在下载第{len(video_urls_list) - i}/{len(video_urls_list)}个---------------------------{video_name_list[i]}')
                print(f'"{nickname}"全部下载完成!')
            video_name_list.clear()
            video_urls_list.clear()
            already_video_name_list.clear()
            if len(download_failed_list):
                print('因超时下载失败的有:')
                print('*' * 50)
                for j in download_failed_list:
                    print('- ' + j)
                print('共下载失败:' + str(len(download_failed_list)) + '个.')
                print('*' * 50)
                download_failed_list.clear()
    print('全部下载完成!')
    end = time.time()
    print(end - start)
