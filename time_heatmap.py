#!/usr/bin/env python3
"""
[url] https://tb.antiscroll.com
[author] https://github.com/tategakibunko
[license] MIT
"""
import sys, time
import numpy as np
from scipy.stats import entropy
from corpus import html2corpuses
from is_time import is_time_words

"""
[usage]

cat foo.txt | ./time_heatmap.py
"""
def print_score(corpuses):
  time_maps = [is_time_words(words) for words in corpuses]
  total = np.sum(time_maps)
  if total <= 0:
    print("score: 0\n")
    return 0
  sentence_size = len(time_maps)
  hist = np.array_split(time_maps, 10)
  hist = [np.sum(h) for h in hist]
  entpy = entropy(hist, base=2)
  score = (total * entpy) / sentence_size
  print(hist)
  print("score: %f(sentence_size = %d, total = %d, entropy = %f)\n" %
        (score, sentence_size, total, entpy))
  return score

if __name__ == '__main__':
  text = sys.stdin.read()
  corpuses = html2corpuses(text)
  print_score(corpuses)
