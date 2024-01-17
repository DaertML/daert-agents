from urllib.request import urlopen
import os
from bs4 import BeautifulSoup

from jinja2 import Template
import json
import requests

DEFAULT_ACTION = 0
urlllm = "http://localhost:8080/completion"

def llamacpp_generate(urlllm, prompt, temp=0.6):
    headers = {"Content-Type": "application/json"}
    data = {"prompt": prompt, "temperature": temp, "n_predict":-1}
    data = json.dumps(data)
    res = requests.post(url=urlllm, data=data, headers=headers)
    return res.json()["content"]

def download_plain(url):
  html = urlopen(url).read()
  soup = BeautifulSoup(html, features="html.parser")

  for script in soup(["script", "style"]):
    script.extract()

  text = soup.get_text()

  lines = (line.strip() for line in text.splitlines())
  chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
  text = '\n'.join(chunk for chunk in chunks if chunk)

  return text

def download_text(url):
  response = requests.get(url)
  soup = BeautifulSoup(response.text, "html.parser")

  plain_text = []

  for element in soup.find_all(text=True):
      if element.parent.name not in ["script", "style"] and element.strip():
        plain_text.append(element)

  plain_text = "\n".join(plain_text)
  return plain_text


print("I'm Data hungry! Feed me some data :)")
print("Choose between the following options:")
print(" - Press 'f' to feed me data from a file.")
print(" - Press 'd' to paste me some data directly.")
print(" - Press 'u' to get data from a URL.")
print("You can also leave and visit me later by pressing 'q' :(")

while True:
  choice = input("Choice:")
  if choice == 'q':
    print("See ya then! Come back with some juicy data!")
    os._exit(0)

  elif choice == 'd':
    contents = []
    print("Dont forget to press Ctrl+D to let me start digesting...")
    while True:
      try:
        line = input()
      except EOFError:
        break
      contents.append(line)
    prompt = "\n".join(contents)

  elif choice == 'f':
    f = input("Great! I will dive into jummy data! Let me know the filepath:")
    try:
      prompt = open(f, "r").read()
    except:
      print("Don't fool me! That aint no file mate!")
      continue

  elif choice == 'u':
    url_surf = input("The Internet! Here we go!! Where are we headed?")
    prompt = download_text(url_surf)
    metaprompt = "Make a summary in a bullet list of the different news given in CONTENT. Fix any mispelling or words that got plugged together, give it a bit of narrative. CONTENT: "+prompt
    metaprompt += "\nANSWER:"
    #print(metaprompt)
    res = llamacpp_generate(urlllm, metaprompt)
    print(res)
    print("----------------------------------------------------------------------------")
    continue

  else:
    print("Im data hungry!!")
    continue
  metaprompt = open("prompt-summarize.txt", "r").read()
  metaprompt = metaprompt.replace("{data}", prompt)
  res = llamacpp_generate(urlllm, metaprompt)
  print(res)
  print("----------------------------------------------------------------------------")

