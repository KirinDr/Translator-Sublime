import sublime
import sublime_plugin
import re
import http.client
import hashlib
import urllib
import random
import json
from .config import appid, secretKey


def baidu_translate(word):
    myurl = 'http://api.fanyi.baidu.com/api/trans/vip/translate'

    from_lang = 'auto'
    to_lang = 'en'
    salt = random.randint(32768, 65536)
    sign = appid + word + str(salt) + secretKey
    sign = hashlib.md5(sign.encode(encoding="utf-8")).hexdigest()
    
    data = {
        'from': from_lang,
        'to': to_lang,
        'appid': appid,
        'salt': str(salt),
        'sign': sign,
        'q': word
    }
    data = urllib.parse.urlencode(data)
    url = '%s?%s' % (myurl, data)
    res = urllib.request.urlopen(url)
    result = str(res.read(), encoding='utf-8')
    result = json.loads(result)
    if result.get('error_code') is None:
        return result['trans_result'][0]['dst']
    elif result.get('error_code') == '52003':
        sublime.error_message('错误的appid')
    else:
        return None
        


class LineTranslatorCommand(sublime_plugin.TextCommand):

    def is_chinese(self, ch):
        if type(ch) != str: return False
        return '\u4e00' <= ch <= '\u9fff'

    def translate_and_replace(self, edit, region, prefix, string):
        result = baidu_translate(string)
        dst = baidu_translate(string)
        if dst:
            self.view.replace(edit, region, prefix + dst)

    def check_key(self):
        if appid == '' or secretKey == '':
            sublime.error_message('请前往api.fanyi.baidu.com申请appid和secretKey,并添加在config.py')
            return False
        return True

    def run(self, edit):
        if not self.check_key():
            return

        line_region = self.view.line(self.view.sel()[0])
        line_string = self.view.substr(line_region)
        for ch in line_string:
            if self.is_chinese(ch):
                index = line_string.find(ch)
                chinese_string = line_string[index:]
                prefix = '' if index == 0 else line_string[0: index]
                self.translate_and_replace(edit, line_region, prefix, chinese_string)
                return


