from langchain_community.agent_toolkits import GmailToolkit
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langgraph.graph import StateGraph, START, END
from typing import Annotated
from langchain.messages import HumanMessage
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langchain_community.tools.gmail.utils import (build_resource_service,get_gmail_credentials)
from retrieval import email
load_dotenv()

class State(TypedDict):
    messages: Annotated[list, add_messages]
llm  = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    
)
credentials = get_gmail_credentials(
        token_file="token.json",
        scopes=["https://mail.google.com/"],
        client_secrets_file="credentials.json",
    )
api_resource = build_resource_service(credentials=credentials)
toolkit = GmailToolkit(api_resource=api_resource)
tools = toolkit.get_tools()
agent_executor = create_agent(llm, tools)
def queryNode(state: State):

    user_message = state["messages"][-1].content

    retrieval_result = email(query=user_message)

    return {
        "messages": [HumanMessage(content=retrieval_result)]
    }
def agent_node(state: State):

    response = agent_executor.invoke(
        {"messages": state["messages"]}
    )

    return {"messages": response["messages"]}


graph_builder = StateGraph(State)

# node
graph_builder.add_node("query_node", queryNode)
graph_builder.add_node("email_agent", agent_node)

graph_builder.add_edge(START, "query_node")
graph_builder.add_edge("query_node", "email_agent")
graph_builder.add_edge("email_agent", END)


graph = graph_builder.compile()


def email_worker(query):

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("The environment variable is not set")
    config = {
        "configurable":{
            "thread_id":"khush"
        }
    }    
    initial_state = {
            "messages": [HumanMessage(content=query)]
        }

    response = graph.invoke(State(initial_state)
        ,
        config=config
    )

    final_message = response["messages"][-1].content

    return final_message

