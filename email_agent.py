from langchain_community.agent_toolkits import GmailToolkit
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langgraph.graph import StateGraph, START, END, MessagesState
from langchain.messages import HumanMessage, SystemMessage
from langgraph.checkpoint.mongodb import MongoDBSaver
from langchain_community.tools.gmail.utils import (build_resource_service,get_gmail_credentials)
from retrieval import email
load_dotenv()

class State(MessagesState):
    pass
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
def router_node(state: State):
    """
    Decide which node should handle the user query.
    Returns 'query_node' if retrieval is needed,
    'normal_llm' if it can be handled directly by the LLM.
    """
    user_message = state["messages"][-1].content

    decision = llm.invoke([
        SystemMessage(content="""
You are a router for an AI email assistant.

Return ONLY one of these words exactly:
query_node → if the query requires product/email context from retrieval
normal_llm → if the query is general or conversational and does NOT need retrieval
"""),
        HumanMessage(content=user_message)
    ])

    # Normalize
    route = decision.content.strip().lower()
    if "query_node" in route:
        route = "query_node"
    else:
        route = "normal_llm"

    return {"route": route}

def normal_llm(state: State):
    """
    Handles general queries using the entire conversation in state["messages"].
"""
    response = llm.invoke(state["messages"])
    return {"messages": [response]}
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

# Add nodes
graph_builder.add_node("router_node", router_node)
graph_builder.add_node("query_node", queryNode)
graph_builder.add_node("email_agent", agent_node)
graph_builder.add_node("normal_llm", normal_llm)


graph_builder.add_edge(START, "router_node")


graph_builder.add_conditional_edges(
    "router_node",
    lambda state: state["route"],
    {
        "query_node": "query_node",
        "normal_llm": "normal_llm"
    }
)


graph_builder.add_edge("query_node", "email_agent")


graph_builder.add_edge("email_agent", END)
graph_builder.add_edge("normal_llm", END)
def compile_graph_with_checkpointer(checkpointer):
    return graph_builder.compile(checkpointer=checkpointer)



def email_worker(query):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set")

    config = {"configurable": {"thread_id": "khush"}}

    initial_state = {"messages": [HumanMessage(content=query)]}
    DB_URI = os.getenv("MONGODB_URI")
    with MongoDBSaver.from_conn_string(DB_URI) as checkpointer:
        graph_with_checkpointer = compile_graph_with_checkpointer(checkpointer=checkpointer)
        config = {
        "configurable":{
            "thread_id":"khush"
        }
    }    

        response = graph_with_checkpointer.invoke(initial_state, config=config)

        return response["messages"][-1].content

