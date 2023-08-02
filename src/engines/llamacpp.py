import os
class LlamaEngine:
	def __init__(self, llamacpp_path, model_path):
		self.llamacpp_path = llamacpp_path
		self.model_path = model_path

	def run(self, prompt):
		os.system(self.llamacpp_path+" -m "+self.model_path+" -p \""+prompt+"\" > devres.txt")
		print(open("devres.txt", "r").read())
		os.system("rm devres.txt")

if __name__ == "__main__":
	llm = LlamaEngine("/home/llama/llama.cpp/build/bin/main", "/home/llama/llama.cpp/models/nous-hermes-llama-2-7b.ggmlv3.q4_0.bin")
	llm.run("Explain step by step how to fill a glass with water:")
