import os
import argparse
import json
import requests
parser = argparse.ArgumentParser(
                    prog='Code Companion',
                    description='LLM answers questions based on the context provided by the user.',
                    epilog='Pair program with your favourite AI.')

parser.add_argument('-p', '--prompt', default="webdev.txt")
parser.add_argument('-d', '--base_dir', default=".")
parser.add_argument('-f', '--formats', default="js,html,ts,css,json")
args = parser.parse_args()

urlllm = "http://localhost:8080/completion"

def llamacpp_generate(urlllm, prompt, temp=0.6):
    headers = {"Content-Type": "application/json"}
    data = {"prompt": prompt, "temperature": temp}
    data = json.dumps(data)
    res = requests.post(url=urlllm, data=data, headers=headers)
    return res.json()["content"]

formats = args.formats.split(",")
base_dir = args.base_dir
prompt_file = args.prompt

prompt = open(prompt_file, "r").read()

for root, dirs, files in os.walk(base_dir):
    for file in files:
        if file.split(".")[-1] in formats:
            relative_path = os.path.relpath(os.path.join(root, file), base_dir)
            prompt += "Filepath: " + relative_path + "\n"
            prompt += "Content:\n" + open(os.path.join(root,file), "r").read() +"\n"

prompt += "</context>\n\n"
print(prompt)
prompt += "Question:\n"
prompt += input("Question:\n")

resp = llamacpp_generate(urlllm, prompt)
print("Response:\n")
print(resp)
