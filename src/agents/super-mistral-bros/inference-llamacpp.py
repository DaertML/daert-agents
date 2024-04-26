import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import time
from nes_py.wrappers import JoypadSpace
import gym_super_mario_bros
from PIL import Image
import cv2
import numpy as np
import os
from gym_super_mario_bros.actions import SIMPLE_MOVEMENT
env = gym_super_mario_bros.make('SuperMarioBros-v0')
env = JoypadSpace(env, SIMPLE_MOVEMENT)

from pydantic import BaseModel, validator

actions = {}
actions["NOOP"] = 0
actions["WALK-RIGHT"] = 1
actions["JUMP-WALK-RIGHT"] = 2
actions["RUN-RIGHT"] = 3
actions["JUMP-RUN-RIGHT"] = 4
actions["JUMP"] = 5
actions["WALK-LEFT"] = 6

class ActionModel(BaseModel):
    action: str

    # Validator to ensure action takes one of the specified values
    @validator('action')
    def validate_action(cls, v):
        if v not in ("RUN-RIGHT", "JUMP", "RUN-LEFT"):
            raise ValueError('Action must be "RUN-RIGHT", "JUMP", or "RUN-LEFT"')
        return v

def respond(query):
    eval_prompt = """Given the following screen of Super Mario Bros, decide which action to take. Just output the action, which can be
                     either RUN-RIGHT, WALK-RIGHT, WALK-LEFT, JUMP-RUN-RIGHT, JUMP-WALK-RIGHT. \n\n {} \n\nACTION: """.format(query)

    model_input = tokenizer(eval_prompt, return_tensors="pt").to("cuda")
    output = ft_model.generate(input_ids=model_input["input_ids"].to("cuda"),
                           attention_mask=model_input["attention_mask"], 
                           max_new_tokens=125, repetition_penalty=1.15)
    result = tokenizer.decode(output[0], skip_special_tokens=True).replace(eval_prompt, "")
    return result

def load_image(image_path):
    # Load an image in grayscale
    return cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

def pixel_to_ascii(image):
    # Map grayscale values to ASCII characters
    ascii_chars = "@%#*+=-:. "
    new_image = []
    for row in image:
        new_image.append(''.join([ascii_chars[pixel//32] for pixel in row]))
    return "\n".join(new_image)

base_model_id = "mistralai/Mistral-7B-v0.1"
#bnb_config = BitsAndBytesConfig(
#    load_in_4bit=True,
#    bnb_4bit_use_double_quant=True,
#    bnb_4bit_quant_type="nf4",
#    bnb_4bit_compute_dtype=torch.bfloat16
#)

base_model = AutoModelForCausalLM.from_pretrained(
    base_model_id,  # Mistral, same as before
    #quantization_config=bnb_config,  # Same quantization config as before
    device_map="auto",
    trust_remote_code=True
)

tokenizer = AutoTokenizer.from_pretrained(base_model_id, add_bos_token=True, trust_remote_code=True)

from peft import PeftModel
ft_model = PeftModel.from_pretrained(base_model, "/home/pc/Desktop/LLaMA-Factory/saves/Mistral-7B/lora/train_2024-03-25-22-22-32")

#ft_model.merge_and_unload()
#output_merged_dir = "super-mario-7b"
#os.makedirs(output_merged_dir, exist_ok=True)
#ft_model.save_pretrained(output_merged_dir, safe_serialization=True)


img_size = 32, 64

done = True
action = "NOOP"
for step in range(5000):
    if done:
        state = env.reset()

    env.render()
    img = env.render(mode='rgb_array')
    thumbnail = Image.fromarray(img).convert('L')
    thumbnail.thumbnail(img_size, Image.Resampling.LANCZOS)
    #thumbnail = np.asarray( thumbnail, dtype="int32" )
    thumbnail.save("thumbnail.png", "PNG")
    thumbnail = load_image("thumbnail.png")

    #img = cv2.cvtColor(thumbnail, cv2.COLOR_BGR2GRAY)
    res = pixel_to_ascii(thumbnail)
    print(res)
    action = respond(res)
    print(action)
    state, reward, done, info = env.step(actions[action.strip()])
    print(action)

env.close()