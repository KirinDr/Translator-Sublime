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
        result_s = []
        for s in result['trans_result']:
            result_s.append(s['dst'])
        result_s = '\n'.join(result_s)
        return result_s
    elif result.get('error_code') == '52003':
        sublime.error_message('错误的appid')
    else:
        return None


class LineTranslatorCommand(sublime_plugin.TextCommand):
    print('translator正在将中文翻译为英文...')
    def is_chinese(self, ch):
        if type(ch) != str: return False
        return '\u4e00' <= ch <= '\u9fff'

    def check_key(self):
        if appid == '' or secretKey == '':
            sublime.error_message('请前往api.fanyi.baidu.com申请appid和secretKey,并添加在config.py')
            return False
        return True

    def translate(self, region, prefix, string):
       dst = baidu_translate(string)
       if dst:
          self.view.run_command('replace', {'region': (region.a, region.b), 'string': prefix + dst})

    def run(self, edit):
        if not self.check_key():
            return

        only_line = False

        choose_line = self.view.sel()[0]
        if choose_line.a == choose_line.b:
            only_line = True

        if only_line:
            region = self.view.line(choose_line)
            line_string = self.view.substr(region)
            for ch in line_string:
                if self.is_chinese(ch):
                    index = line_string.find(ch)
                    chinese_string = line_string[index:]
                    prefix = '' if index == 0 else line_string[0: index]
                    break
        else:
            region = choose_line
            chinese_string = self.view.substr(region)
            prefix = ''

        sublime.set_timeout_async(lambda :self.translate(region, prefix, chinese_string), 0)


class ReplaceCommand(sublime_plugin.TextCommand):
    def run(self, edit, region, string):
        region = sublime.Region(region[0], region[1])
        self.view.replace(edit, region, string)