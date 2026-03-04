from langchain_community.agent_toolkits import GmailToolkit
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langchain_community.tools.gmail.utils import (build_resource_service,get_gmail_credentials)
from retrieval import email
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("The environment variable is not set")
llm = ChatGoogleGenerativeAI(model = "gemini-2.0-flash")

credentials = get_gmail_credentials(
    token_file="token.json",
    scopes=["https://mail.google.com/"],
    client_secrets_file="credentials.json",
)
api_resource = build_resource_service(credentials=credentials)
toolkit = GmailToolkit(api_resource=api_resource)


tools = toolkit.get_tools()
agent_executor = create_agent(llm, tools)

query = "send an email to eklavyapopli@gmail.com sending the list of products and asking if they are interested or not. it should be professional and properly structured with new lines and spaces whereever needed"
email_query = email(query=query)

events = agent_executor.stream(
    {"messages": [("user", email_query)]},
    stream_mode="values",
)
for event in events:
    event["messages"][-1].pretty_print()

