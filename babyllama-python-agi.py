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
	print("CODE BEFORE", code)
	#code = code.replace(prompt, "")
	code = "".join(code[1:])
	print("CODE AFTER", code)
	code_f.close()
	return code

#Other ways ot delimiting the prompt and the code:
# Use " ""code" "" to make sure that the prompt feels like a python string
# Use <prompt> </prompt> to write the prompt and then remove it
# Use a single line for the prompt, and then only go from 1: lines
# Use # for each line of the prompt to make it a comment

prompt = """\"You are a skilled developer, write working python code to create tasks \
in a SQL Lite DB. Each task contains a name, a description, and a list of parameters; \
the list of parameters is a comma separated string with the parameters names. Any additional \
comment or explanation should be inside a python comment:
\""""

prompt = """#You are a skilled developer, write working python code directly, to sum two numbers and print the result.\n"""

call_llama(prompt)
code = get_code(prompt)

while True:
	try:
		print("Executing...")
		print(code)
		#time.sleep(10)
		exec(code)
		print("Code executed")
		break
	except Exception as error:
		print(error)
		print("====================================")
		time.sleep(2)
		fix_prompt = '\"<prompt>The python code in between <code> and </code> is not working, try to fix it: \n\""""<code>""""\n'+code+'\n"""</code>"""</prompt>'
		call_llama(fix_prompt)
		code = get_code(fix_prompt)
		print(code)
