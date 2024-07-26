import requests
from langchain.agents import Tool, AgentExecutor, create_structured_chat_agent
from langchain.prompts import StringPromptTemplate, PromptTemplate
from langchain.chains import LLMChain
from langchain.schema import AgentAction, AgentFinish
from typing import List, Union, Dict
import re
from langchain_groq import ChatGroq
from groq import Groq
import os

from dotenv import load_dotenv
load_dotenv()

groq_api_key = os.environ["GROQ_API_KEY"]

# Define the base URL for your FastAPI application
BASE_URL = "http://localhost:8000"

# Define tools for the agent
def get_item_details(item_number: int) -> str:
    response = requests.get(f"{BASE_URL}/items/{item_number}")
    if response.status_code == 200:
        item = response.json()
        return f"Item Number: {item['item_number']}, Item Name: {item['item_name']}, Value: {item['value']}"
    else:
        return f"Error: Item {item_number} not found"

def delete_item(item_number: str) -> str:
    response = requests.delete(f"{BASE_URL}/items/{item_number}")
    if response.status_code == 200:
        return f"Item {item_number} deleted successfully"
    else:
        return f"Error: Item {item_number} not found"

tools = [
    Tool(
        name="GetItemDetails",
        func=get_item_details,
        description="Useful for getting details about an item by its item number"
    ),
    Tool(
        name="DeleteItem",
        func=delete_item,
        description="Useful for deleting an item by its item number"
    )
]

# Define a custom prompt template
template = """You are an AI assistant that helps with managing inventory items.
You have access to the following tools:

Tools: {tools}

Tool names: {tool_names}

Please keep track of your thoughts and action here: {agent_scratchpad}

Use the following format:

Command: <command name>
Item Number : <item number>

Response:
<response>

If the command is not recognized, response with "Unknown Command."

"""


class PromptTemplate(StringPromptTemplate):
    def format(self, **kwarg)->str:
        tools_info = "\n".join([f"{tool.name}: {tool.description}" for tool in tools])
        tool_names = ", ".join([tool.name for tool in tools])
        return template.format(tools=tools_info, tool_names=tool_names)


#Definr the prompt template
prompt = PromptTemplate(input_variables=["input_text"], template=template)


llm = ChatGroq(
    model="llama-3.1-8b-instant",
)

#runnable_sequence = prompt | llm

"""
#output parser
def parse_output(output: str) -> Union[AgentAction, AgentFinish]:
    command_match = re.search(r"Command:\s*(\w+)", output)
    item_number_match = re.search(r"Item Number:\s*(\d+)", output)
    
    if not command_match or not item_number_match:
        return AgentFinish(message="Unknown command", log=output)

    command = command_match.group(1)
    item_number = int(item_number_match.group(1))
    
    for tool in tools:
        if tool.name == command:
            return AgentAction(tool=tool, inputs={"item_number": item_number})
    
    return AgentFinish(message="Unknown command", log=output)

"""
#Agent executor
agent = create_structured_chat_agent(
    prompt=prompt,
    llm = llm,
    tools=tools,
    #parse_output=parse_output
)
executor = AgentExecutor(agent=agent, tools = tools)

#executor 
input_text = "get details of itrm number 110."
response = executor.run(input_text)
print(response)