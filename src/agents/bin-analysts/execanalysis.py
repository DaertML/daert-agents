from langchain_core.tools import tool, BaseTool
from langchain.pydantic_v1 import BaseModel, Field

MODEL="llama3.1"
#MODEL="llama3-groq-tool-use"
#MODEL="mistral:7b"
#MODEL="llama3.2"
#MODEL="qwen2.5:32b"

class BinaryAnalysisInput(BaseModel):
    binary_path: str = Field(description="path to the binary program to analyze")

class StringsToolInput(BinaryAnalysisInput):
    pass

class FileToolInput(BinaryAnalysisInput):
    pass

class ObjdumpToolInput(BinaryAnalysisInput):
    pass

@tool(args_schema=StringsToolInput)
def strings_tool(binary_path: str) -> str:
    """Analyze binary using the 'strings' command."""
    import subprocess
    result = subprocess.run(["strings", binary_path], capture_output=True, text=True)
    return result.stdout

@tool(args_schema=FileToolInput)
def file_tool(binary_path: str) -> str:
    """Analyze binary using the 'file' command."""
    import subprocess
    result = subprocess.run(["file", binary_path], capture_output=True, text=True)
    return result.stdout

@tool(args_schema=ObjdumpToolInput)
def objdump_tool(binary_path: str) -> str:
    """Analyze binary using the 'objdump' command."""
    import subprocess
    result = subprocess.run(["objdump", "-d", binary_path], capture_output=True, text=True)
    return result.stdout

from langchain_core.tools import tool
from langchain_ollama import ChatOllama

#from langchain_community.chat_models import ChatOpenAI
from langchain_openai import OpenAI, ChatOpenAI


#llm = ChatOllama(model=MODEL)

llm = ChatOpenAI(
    api_key="ollama",
    model=MODEL,
    base_url="http://localhost:11434/v1",
).bind_tools([objdump_tool, strings_tool])

from langchain_core.tools import render_text_description
from langchain.agents import AgentExecutor, create_react_agent, create_tool_calling_agent
from langchain import hub

tools = [strings_tool, file_tool, objdump_tool]
prompt = hub.pull("hwchase17/react-json")

prompt = prompt.partial(
    tools=render_text_description(tools),
    tool_names=", ".join([t.name for t in tools]),
)

binanal_role = """
You are a binary analyst; you are an expert in analyzing program binaries and finding out details about them.
Your research is useful to identify malicious or anomalous programs.

Use your available tools to get insights about the program and follow the user requests.
Do not hallucinate the output of the tools.
Do not imagine the output of the tool, just call the tool that you consider best for the situation.

User: analyze the file at path ./a.out and let me know a summary of the findings. Use the strings tool. Give me 5 examples of the output of the strings command.
"""

agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
res = agent_executor.invoke({"input":binanal_role})
print(res)
