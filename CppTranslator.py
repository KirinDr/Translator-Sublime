import sublime
import sublime_plugin
import json
import re
import urllib.request
import urllib.parse


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


def find_note(s):
    pattern = re.compile('/\*(.*?)\*/')
    ret = re.findall(pattern, s)
    pattern = re.compile('//(.*?)\n')
    ret += (re.findall(pattern, s))
    return ret


class CppTranslatorCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        file_name = self.view.file_name()
        with open(file_name, 'r') as f:
          content = f.read()
        notes = find_note(content)
        # self.view.insert(edit, 0, str(notes))
        for note in notes:
            start = self.view.find(note, 0)
            self.view.replace(edit, start, youdao_translate(note))

