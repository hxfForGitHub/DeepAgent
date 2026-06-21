from langchain_openai import ChatOpenAI

from agent.env_utils import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL

llm = ChatOpenAI(
    model="deepseek-chat",
    temperature=1.0,
    openai_api_key=DEEPSEEK_API_KEY,
    openai_api_base=DEEPSEEK_BASE_URL,
)
