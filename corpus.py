"""
[url] https://tb.antiscroll.com
[author] https://github.com/tategakibunko
[license] MIT
"""
import re
import sys
import pprint
import MeCab as Me
import requests
from bs4 import BeautifulSoup as BSoup

debug_mecab = False

rex_phrase_delim = re.compile('[\n。！]')
rex_ruby1 = re.compile(r'<ruby>(?:<rb>)?(.*?)(?:</rb>)?<rt>.+</rt></ruby>')
rex_ruby2 = re.compile(r'<ruby><rt>.+</rt>(?:<rb>)?(.*?)(?:</rb>)?</ruby>')
rex_local_tag = re.compile(r'\[[a-z\-]+([^]]*)\]')
rex_aozora_tag = re.compile(r'［＃.+］')
rex_markdown_header = re.compile(r'#+')
rex_space = re.compile(r'[\u3000]+')
rex_alpha = re.compile(r'[a-zA-Z@]+')

me_parser = Me.Tagger("-Ochasen")

stemming_words = [
  'ある', 'なる', 'ない', 'する', 'できる',
  '!?', '!!', '!', '?!', '??',
]

def normalize_ruby(html):
  if re.search(rex_ruby1, html):
    return re.sub(rex_ruby1, r'\1', html)
  if re.search(rex_ruby2, html):
    return re.sub(rex_ruby2, r'\1', html)
  return html

def normalize_spec_tag(html):
  html = re.sub(rex_local_tag, r'\1', html)
  html = re.sub(rex_aozora_tag, '', html)
  return html

def normalize_markdown(html):
  return re.sub(rex_markdown_header, '', html)

def normalize_space(html):
  return re.sub(rex_space, '', html)

def is_stop_word(word):
  if word in stemming_words:
    return True
  if re.match(rex_alpha, word):
    return True
  return False

def pickup_feature(feature):
  parts = feature.split('\t')
  if debug_mecab:
    print(parts)
  if len(parts) <= 4:
    return ''
  word = parts[2]
  info = parts[3].split('-')
  ext = parts[-1];
  desc = info[0];
  if desc in ['名詞', '形容詞']:
  # if desc in ['名詞', '形容詞', '副詞']:
    if ext in ['連用形', '未然レル接続']:
      return ''
    # if len(info) > 1 and info[1] in ['代名詞', '接尾', '非自立']:
    if len(info) > 1 and info[1] in ['代名詞', '非自立']:
      return ''
    if is_stop_word(word):
      return ''
    return word
  return ''

def html2text(html):
  html = normalize_ruby(html)
  html = normalize_spec_tag(html)
  html = normalize_markdown(html)
  html = normalize_space(html)
  soup = BSoup(html, features="html.parser")
  return soup.text

def text2phrases(text):
  return list(re.split(rex_phrase_delim, text))

def phrase2feature(phrase):
  parts = me_parser.parse(phrase).split('\n')
  parts = map(pickup_feature, parts)
  return list(filter(lambda x: x != '', parts))

def phrase2corpus(phrase):
  phrase = phrase.strip()
  return phrase2feature(phrase)

def html2corpuses(html):
  text = html2text(html)
  phrases = text2phrases(text)
  corpus_list = [phrase2corpus(p) for p in phrases]
  corpus_list = list(filter(lambda c: len(c) > 0, corpus_list))
  return corpus_list

