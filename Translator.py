import sublime
import sublime_plugin
import json
import re
import urllib.request
import urllib.parse


def cancel_RegEx(string):
    # 取消正则关键字
    key = ['\\', '.', '*', '^', '&', '[', ']', '{', '}', '?']
    ret = ''
    for ch in string:
        if ch in key:
            ret += '\\' + ch
        else:
            ret += ch
    return ret



def youdao_translate(word):
    url = 'http://fanyi.youdao.com/translate?smartresult=dict&smartresult=rule&smartresult=ugc&sessionFrom=null'
    key = {
        'type': "AUTO",
        'i': word,
        "doctype": "json",
        "version": "2.1",
        "keyfrom": "fanyi.web",
        "ue": "UTF-8",
        "action": "FY_BY_CLICKBUTTON",
        "typoResult": "true"
    }
    data = urllib.parse.urlencode(key)
    request = urllib.request.Request(url, data.encode())
    openreq = urllib.request.urlopen(request)
    dic = json.loads(openreq.read().decode())
    tgt = dic['translateResult'][0][0]['tgt']
    return tgt


class CppTranslatorCommand(sublime_plugin.TextCommand):

    def find_note(self, s):
        pattern = re.compile('/\*(.*?)\*/')
        ret = re.findall(pattern, s)
        pattern = re.compile('//(.*?)\n')
        ret += (re.findall(pattern, s))
        return ret

    def run(self, edit):
        file_name = self.view.file_name()
        with open(file_name, 'r') as f:
          content = f.read()
        notes = self.find_note(content)
        for note in notes:
            start = self.view.find(cancel_RegEx(note), 0)
            self.view.replace(edit, start, youdao_translate(note))


class LineTranslatorCommand(sublime_plugin.TextCommand):

    def is_chinese(self, ch):
        if type(ch) != str: return False
        return '\u4e00' <= ch <= '\u9fff'

    def translate(self, edit, string):
        result = youdao_translate(string)
        start = self.view.find(cancel_RegEx(string), 0)
        self.view.replace(edit, start, youdao_translate(string))


    def run(self, edit):
        line_region = self.view.line(self.view.sel()[0])
        line_string = self.view.substr(line_region).strip()
        for ch in line_string:
            if self.is_chinese(ch):
                index = line_string.find(ch)
                chinese_string = line_string[index:]
                self.translate(edit, chinese_string)
                return


