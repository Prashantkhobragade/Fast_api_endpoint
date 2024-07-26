import requests
from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent
from langchain.prompts import StringPromptTemplate
from langchain.chains import LLMChain
from langchain.schema import AgentAction, AgentFinish
from typing import List, Union, Dict
import re
from langchain_groq import ChatGroq
from groq import Groq

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

{tools}

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
        return template.format(tools=tools_info)
    

#Definr the prompt template
prompt = PromptTemplate(input_variables=["input_text"])

llm = Groq()
print(llm)