import os
import time

#run = True
#def stop():
#	run = False
#keyboard.add_hotkey("shift+c", stop)

def call_llama(prompt):
	os.system("/home/llama/llama.cpp/build/bin/main -m /home/llama/llama.cpp/models/nous-hermes-llama-2-7b.ggmlv3.q4_0.bin -p \""+prompt+"\" > devres.txt")

def get_code(prompt):
	code_f = open("devres.txt", "r")
	code = code_f.readlines()
	#code = code.replace(prompt, "")
	code = "".join(code[1:])
	code_f.close()
	return code

#Other ways ot delimiting the prompt and the code:
# Use " ""code" "" to make sure that the prompt feels like a python string
# Use <prompt> </prompt> to write the prompt and then remove it
# Use a single line for the prompt, and then only go from 1: lines
# Use # for each line of the prompt to make it a comment

prompt = """You are a skilled developer, write working python code to create tasks \
in a SQL Lite DB. Each task contains a name, a description, and a list of parameters; \
the list of parameters is a comma separated string with the parameters names. Any additional \
comment or explanation should be inside a python comment:
"""

#prompt = """#You are a skilled developer, write working python code directly, to sum two numbers and print the result.\n"""

while True:
	try:
		call_llama(prompt)
		code = get_code(prompt)
		print("[ ] Executing...")
		print(code)
		#time.sleep(10)
		exec(code)
		print("[*] Code executed")
		res = input("[?] Is it fine? (Y/N)")
		if res == "Y":
			break
		else:
			human_fix = input("[?] Do you want to fix it?(Y/N)")
			if human_fix == "Y":
				fix = input("[] Write the code to append:")
				code += "\n"+fix
			else:
				more_tasks = input("[] Provide more steps:")
				call_llama(more_tasks)
				code += "\n"+get_code(more_tasks)
			print("[ ] Executing Human fix...")
			exec(code)
			print("[*] Human Fix executed.")
	except Exception as error:
		try:
			print(error)
			print("====================================")
			time.sleep(2)
			fix_prompt = 'The python code in between <code> and </code> is not working, try to fix it: \n\""""<code>""""\n'+code+'\n"""</code>""". It is giving the error: '+str(error)+"."
			call_llama(fix_prompt)
			code = get_code(fix_prompt)
			print("Trying fix...")
			print(code)
			exec(code)
			print("Fix executed.")
		except:
			advice = input("[?] Any advice?")
			if advice == "restart":
				continue
			else:
				prompt += advice
			continue
