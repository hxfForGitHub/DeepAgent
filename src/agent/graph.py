"""LangGraph Server 入口——不带 checkpointer，由服务端管理。"""

from deepagents import create_deep_agent

from agent.my_llm import llm
from agent.my_tools import web_search

agent = create_deep_agent(
    model=llm,
    tools=[web_search],
    system_prompt='你是一个助手，请根据用户输入的指令，进行相应的操作。'
)
