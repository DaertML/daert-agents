import gym
import torch
from jinja2 import Template
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import argparse

parser = argparse.ArgumentParser(
                    prog='FrozenLakeLLMAgent',
                    description='LLM writes code to solve an OpenAI gym environment following natural language description.',
                    epilog='Solves the FrozenLake environment defining a policy')

parser.add_argument('-m', '--model', default="NousResearch/Nous-Hermes-Llama2-13b")
parser.add_argument('-p', '--prompt_file', default="qtable_prompt.txt")
parser.add_argument('-d', '--device', default="cuda")
args = parser.parse_args()

quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16
)

tokenizer = AutoTokenizer.from_pretrained(args.model)
model = AutoModelForCausalLM.from_pretrained(args.model, quantization_config=quantization_config)

DEFAULT_ACTION = 0

def generate_policy(input_text):
  inputs = tokenizer(input_text, return_tensors="pt").to(args.device)

  with torch.backends.cuda.sdp_kernel(enable_flash=True, enable_math=False, enable_mem_efficient=False):
      outputs = model.generate(**inputs, max_new_tokens=2048)

  out_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
  code_lines = []
  found_resp = False
  out_text = out_text.split("\n")

  for l in out_text:
    if found_resp:
      code_lines.append(l)
    if "### Response" in l:
      found_resp = True

  code = "\n".join(code_lines)
  print(code)
  return code

env = gym.make("FrozenLake-v1", render_mode="human")
observation, info = env.reset(seed=42)

file = open(args.prompt_file, "r")
input_text = file.read()
file.close()

policy = generate_policy(input_text)

exec(policy)
policy()
env.close()
