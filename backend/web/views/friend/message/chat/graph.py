import os
from typing import TypedDict, Annotated, Sequence

from django.utils.timezone import now, localtime
from langchain_core.messages import BaseMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.constants import START, END
from langgraph.graph import add_messages, StateGraph
from langgraph.prebuilt import ToolNode


# 定义大模型
class ChatGraph:
    @staticmethod
    def create_app():
        @tool
        def get_time() -> str:
            '''当需要获取当前时间时候调用此函数返回格式[YYYY-MM-DD HH:MM:SS]'''
            return localtime(now()).strftime('%Y-%m-%d %H:%M:%S')

        tools = [get_time]

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
        ).bind_tools(tools)
        # 定义状态维护大模型
        class AgentState(TypedDict):
            messages: Annotated[Sequence[BaseMessage], add_messages]
        # agent逻辑
        def model_call(state:AgentState) -> AgentState:
            res = llm.invoke(state['messages'])
            return {'messages': [res]}

        def should_continue(state:AgentState) -> str:
            last_message = state['messages'][-1]
            if last_message.tool_calls:
                return 'tools'
            return 'end'

        tool_node = ToolNode(tools)

        # 计算流程图
        graph = StateGraph(AgentState)
        graph.add_node('agent', model_call)
        graph.add_node('tools', tool_node)

        graph.add_edge(START, 'agent')
        graph.add_conditional_edges(
            'agent',
            should_continue,
            {
                'tools': 'tools',
                'end': END
            }
        )
        graph.add_edge('tools', 'agent')

        return  graph.compile()