# coding:utf-8

import re, urllib, urllib2, requests, time, datetime, random
from bs4 import BeautifulSoup

login_url = 'http://passport.csdn.net/account/login?from=http://my.csdn.net/my/mycsdn'
content = ['下载看看能不能用',
           '不错，可以使用',
           '不错，写的挺清晰的',
           '收藏，谢谢分享！',
           '资源很好，多谢楼主分享……',
           '非常好用，谢谢了……',
           '很好很强大，感觉非常好',
           '可以用，非常感谢……',
           '值得下载，有帮助',
           '比较有参考价值',
           '还不错，给了我很大帮助'
]


def get_ranom_time():
    return str(int(time.time() * 1000))
    pass


def get_back_csdn_jifen():
    # http请求头
    headers = {"User-Agent": "	Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0",
               "Host": "passport.csdn.net",
               "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
               "Accept-Language": "zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3",
               "Accept-Encoding": "gzip, deflate",
               "Connection": "keep-alive"
    }
    session = requests.session()
    # 在请求之前先请求一遍登录页面获取参数，该参数用于真正登录请求时候作为请求头
    # 参数包括lt和_eventId和execution
    bs = BeautifulSoup(session.get(login_url).text)
    execution = bs.find(attrs={'name': 'execution'})['value']
    lt = bs.find(attrs={'name': 'lt'})['value']

    # 请求参数
    payload = {'username': '********', 'password': '****aaa*******', 'lt': lt, '_eventId': 'submit',
               'execution': execution}
    # make 请求
    req = session.post(login_url, data=payload, headers=headers)
    # 到download页面
    download_page_bs = BeautifulSoup(session.get('http://download.csdn.net/my/downloads').text)
    # 获取我曾将下载过资源的最大页数
    last_page = download_page_bs.find_all(name='a', attrs={'class': 'pageliststy'})[-1]
    last_page_href = last_page.get('href')
    max_page = int(last_page_href[last_page_href.rfind('/') + 1:])

    ajax_post_headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Host': 'download.csdn.net',
        'Referer': 'http://download.csdn.net/detail/amy_9291/7743251',
        'X-Requested-With': 'XMLHttpRequest'
    }
    headers['Host'] = 'download.csdn.net'
    # 遍历每一页
    for page_index in xrange(1, max_page + 1):
        page_url = 'http://download.csdn.net/my/downloads/%s' % page_index
        every_page_bs = BeautifulSoup(session.get(page_url, headers=headers).text)
        comment_list = every_page_bs.find_all('a', {'class': 'btn-comment'})
        for comment in comment_list:
            comment_href = comment.get('href')
            detail_herf = comment_href[0:comment_href.rfind('#')]
            source_id = detail_herf[comment_href.rfind('/') + 1:]  # 获取资源id
            ajax_post_headers['Referer'] = 'http://download.csdn.net' + detail_herf
            headers.update(ajax_post_headers)  # 更新请求头
            detail_name = every_page_bs.find('a', {'href': detail_herf}).get_text()  # 这是哪一本书

            # 下面开始构造请求评价的url
            # 类似这种url= 'http://download.csdn.net/index.php/comment/post_comment?jsonpcallback=jsonp1418779869145&sourceid=6828315&content=%E9%AB4%B5&rating=4&t=1418780239456'
            post_comment_url = 'http://download.csdn.net/index.php/comment/post_comment'
            param_dict = {
                'jsonpcallback': 'json' + get_ranom_time(),
                'sourceid': source_id,
                'rating': random.randint(1, 5),
                'content': random.choice(content),
                't': get_ranom_time()
            }
            print detail_name,'开始评价'
            response = session.get(post_comment_url, params=param_dict)
            res = response.text
            succ_code = res[res.rfind(':') + 1:res.rfind('})')]
            if succ_code == '1' and response.status_code == 200:
                print detail_name, '已经评价'
            else:
                print detail_name, '评价出错', 'succ_code', succ_code
            pass
            time.sleep(random.randint(65, 90))  # sleep一个比较长的时间，因为csdn要求 两次评论需要间隔60秒
        pass
    pass


if __name__ == '__main__':
    get_back_csdn_jifen()
    pass