import os
from typing import TypedDict, Annotated, Sequence

from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.constants import START, END
from langgraph.graph import add_messages, StateGraph

# 定义大模型
class ChatGraph:
    @staticmethod
    def create_app():
        llm = ChatOpenAI(
            model = 'qwen3.6-plus',
            openai_api_key = os.getenv('API_KEY'),
            openai_api_base = os.getenv('API_BASE'),
            streaming=True,  # 流式输出

            model_kwargs = {
            "stream_options": {
                "include_usage": True,  # 输出token消耗数量
            }
        }
        )
        # 定义状态维护大模型
        class AgentState(TypedDict):
            messages: Annotated[Sequence[BaseMessage], add_messages]
        # agent逻辑
        def model_call(state:AgentState) -> AgentState:
            res = llm.invoke(state['messages'])
            return {'messages': [res]}
        # 计算流程图
        graph = StateGraph(AgentState)
        graph.add_node('agent', model_call)

        graph.add_edge(START, 'agent')
        graph.add_edge('agent', END)

        return  graph.compile()