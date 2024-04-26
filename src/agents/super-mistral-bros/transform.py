import cv2
import os
from PIL import Image
import pandas as pd
import json

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

os.system("sudo rm -r thumbset")
os.system("mkdir thumbset")
directory_path = "./dataset"
thumbs_path = "./thumbset"

size = 64, 64

datalist = []

for filename in os.listdir(directory_path):
    if os.path.isfile(os.path.join(directory_path, filename)):
        filepath = os.path.join(directory_path, filename)

        im = Image.open(filepath).convert('L')
        im.thumbnail(size, Image.Resampling.LANCZOS)
        im.save("./thumbset/"+filename.split(".")[0]+".png", "PNG")
        img = load_image("./thumbset/"+filename.split(".")[0]+".png")

        res = pixel_to_ascii(img)
        data = {}
        data["question"] = res
        data["answer"] = "-".join(filename.split(".")[0].split("-")[1:])
        datalist.append(data)
        res += "\nACTION: "+"-".join(filename.split(".")[0].split("-")[1:])

        ascii_file = open("./ascii/"+filename.split(".")[0]+".txt", "w")
        ascii_file.write(res)
        ascii_file.close()

        print(res)

df = pd.DataFrame(datalist)
df.to_csv("./games.csv")
json.dump(datalist, open("./games.json", "w"))

jsonl = open("./games.jsonl", "w")
for elem in datalist:
    jsonl.write(json.dumps(elem)+"\n")
jsonl.close()

jsonl_train = open("./train.jsonl", "w")
jsonl_test = open("./test.jsonl", "w")

train_split = 0.9
test_split = 1-train_split

n_train = int(train_split*len(datalist))

for elem in datalist[:n_train]:
    jsonl_train.write(json.dumps(elem)+"\n")

for elem in datalist[n_train:]:
    jsonl_test.write(json.dumps(elem)+"\n")

jsonl_train.close()
jsonl_test.close()
