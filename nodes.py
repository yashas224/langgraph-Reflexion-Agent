import json
from typing import Literal

from langchain.messages import AIMessage, ToolMessage
from langchain_core.tools import StructuredTool
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt.tool_node import ToolNode

from chains import responder_chain, revisor_chain
from schemas import AnswerQuestion, ReviseAnswer
from tool_executor import run_queries

MAX_ITERATION = 2


def draft_node(state: MessagesState):
    """Draft initial Response"""
    response: AnswerQuestion = responder_chain.invoke(
        {"messages": state.get("messages")}
    )
    queries = response.search_queries
    tool_call = {
        "name": "AnswerQuestion",
        "args": {"searchList": queries},
        "id": "search-AnswerQuestion",
        "type": "tool_call",
    }
    response.search_queries = []
    ai_message = AIMessage(content=response.model_dump_json(), tool_calls=[tool_call])
    return {"messages": [ai_message]}


def revise_node(state: MessagesState):
    """Revise the answer based on tool result"""
    response: ReviseAnswer = revisor_chain.invoke({"messages": state.get("messages")})
    queries = response.search_queries

    tool_call = {
        "name": "ReviseAnswer",
        "args": {"searchList": queries},
        "id": "search-AnswerQuestion",
        "type": "tool_call",
    }
    response.search_queries = []
    ai_message = AIMessage(content=response.model_dump_json(), tool_calls=[tool_call])
    return {"messages": [ai_message]}


def event_loop_edge(state: MessagesState) -> str:
    count_tool_visits = sum(
        1 for msg in state.get("messages") if isinstance(msg, ToolMessage)
    )
    if count_tool_visits > MAX_ITERATION:
        return END
    return "execute_tool"


#  Two tools wtih same function called by two diffent Nodes.
# 1- Draft Node calls the tool to get initial answer
# 2- Revise Node calls the tool to get revised answer based on critique and new information.
tool_node = ToolNode(
    [
        StructuredTool.from_function(run_queries, name=AnswerQuestion.__name__),
        StructuredTool.from_function(run_queries, name=ReviseAnswer.__name__),
    ]
)
