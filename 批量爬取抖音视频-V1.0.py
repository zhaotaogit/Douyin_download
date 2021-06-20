# -*- coding = utf-8 -*-
# @Time : 2021/6/20 0:00
# @File : 批量爬取抖音视频-V1.0.py
# @Software: PyCharm
import requests
import re
import os
import time

start = time.time()
# 用户输入作者主页链接
print('本程序仅用于批量爬取抖音作者的所有视频!若程序出现问题，请联系作者:QQ1787417712')
author_url = input('请输入作者的主页链接:')
# UA代理
headers = {
    'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Mobile Safari/537.36'
}
# 访问作者主页

resp = requests.get(author_url, headers=headers)
# 获取重定向后的作者主页链接
author_url = resp.url


# 根据作者主页链接拿到sec_uid
sec_uid = author_url.split('sec_uid=')[1].split('&')[0]

# 获取作者作品总数和作者名称
number_of_works = 'https://www.iesdouyin.com/web/api/v2/user/info/?sec_uid=' + sec_uid
resp1 = requests.get(number_of_works, headers=headers)
wokrs_count = resp1.json()['user_info']['aweme_count']
author = resp1.json()['user_info']['nickname']

# 创建存放视频的文件夹

path = os.path.join(os.getcwd(), author)
if not os.path.exists(path):
    os.mkdir(path)
print(f'已成功创建文件夹{path},将用于保存视频!')
os.chdir(path)
print('开始下载所有视频')

# 获取作者视频并保存到本地
max_cursor = 0
n = 1
for x in range(wokrs_count // 20):
    # 获取作者作品名和作品链接
    requ_url = 'https://www.iesdouyin.com/web/api/v2/aweme/post/?sec_uid=' + sec_uid + f'&count=21&max_cursor={max_cursor}&aid=1128&_signature=RmgLIQAAJqehH.Mn4SqZZEZoCz&dytk='
    resp2 = requests.get(requ_url, headers=headers)
    rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
    for i in resp2.json()['aweme_list']:
        name = re.sub(rstr, '_', i['desc']) + '.mp4'  # 替换掉不能当做文件名的字符
        href = i['video']['play_addr_lowbr']['url_list'][0]
        with open(f'{n}.{name}', 'wb') as f:
            f.write(requests.get(href, headers=headers).content)
            print(f'{n + 1}.', name, '-------下载完成')
        n += 1
    max_cursor = resp2.json()['max_cursor']
    print(f'第{x + 1}批结束')
end = time.time()
print(end-start)
