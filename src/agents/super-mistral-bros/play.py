import time
from nes_py.wrappers import JoypadSpace
import gym_super_mario_bros
from pynput import keyboard
import matplotlib.pyplot as plt
from PIL import Image
from itertools import product
import os
from gym_super_mario_bros.actions import SIMPLE_MOVEMENT
env = gym_super_mario_bros.make('SuperMarioBros-v0')
env = JoypadSpace(env, SIMPLE_MOVEMENT)

def tile(filename, dir_in, dir_out, d):
    name, ext = os.path.splitext(filename)
    img = Image.open(os.path.join(dir_in, filename))
    w, h = img.size
    
    grid = product(range(0, h-h%d, d), range(0, w-w%d, d))
    for i, j in grid:
        box = (j, i, j+d, i+d)
        out = os.path.join(dir_out, f'{name}_{i}_{j}{ext}')
        img.crop(box).save(out)


actions = {}
actions["NOOP"] = 0
actions["WALK-RIGHT"] = 1
actions["JUMP-WALK-RIGHT"] = 2
actions["RUN-RIGHT"] = 3
actions["JUMP-RUN-RIGHT"] = 4
actions["JUMP"] = 5
actions["WALK-LEFT"] = 6

keys = {}
keys["W"] = "RUN-RIGHT"
keys["w"] = "WALK-RIGHT"
keys["s"] = "WALK-LEFT"
keys["S"] = "WALK-LEFT"
keys["J"] = "JUMP-RUN-RIGHT"
keys["j"] = "JUMP-WALK-RIGHT"

img_size = 32, 64

done = True
action = "NOOP"
for step in range(5000):
    # action = "NOOP"
    if done:
        state = env.reset()
    #state, reward, done, info = env.step(env.action_space.sample())
    #action = env.action_space.sample()
    #if action not in actions:
    #   actions.append(action)
    #time.sleep(0.0333333)
    print("WAITING HERE")
    try:

        with keyboard.Events() as events:
        # Block for as much as possible
           print("OR HERE")
           event = events.get(1)
           if event.key == keyboard.KeyCode.from_char('W'):
              action = "RUN-RIGHT"
           if event.key == keyboard.KeyCode.from_char('w'):
              action = "WALK-RIGHT"
           if event.key == keyboard.KeyCode.from_char('s'):
              action = "WALK-LEFT"
           if event.key == keyboard.KeyCode.from_char('S'):
              action = "WALK-LEFT"
           if event.key == keyboard.KeyCode.from_char('J'):
              action = "JUMP-RUN-RIGHT"
           if event.key == keyboard.KeyCode.from_char('j'):
              action = "JUMP-WALK-RIGHT"
    except:
       continue

    env.render()
    img = env.render(mode='rgb_array')
    image = Image.fromarray(img)
    thumbnail = Image.fromarray(img)
    thumbnail.thumbnail(img_size, Image.Resampling.LANCZOS)
    thumbnail.save("./thumbs/"+str(step)+"-"+str(action)+".png", "PNG")
    image.save("./data/"+str(step)+"-"+str(action)+".png", "PNG")

    state, reward, done, info = env.step(actions[action])
    print(dir(img))
    print(type(img))

    print(action)

env.close()
