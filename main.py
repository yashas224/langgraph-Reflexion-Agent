from langchain.messages import AIMessage, HumanMessage
from langgraph.graph import END, MessagesState, StateGraph

from nodes import draft_node, event_loop_edge, revise_node, tool_node
from schemas import ReviseAnswer


def main():
    print("Hello from langgraph-reflexion-agent!")


builder = StateGraph(state_schema=MessagesState)
builder.add_node("draft", draft_node)
builder.add_node("revise", revise_node)
builder.add_node("execute_tool", tool_node)


builder.set_entry_point("draft")

builder.add_edge("draft", "execute_tool")
builder.add_edge("execute_tool", "revise")


builder.add_conditional_edges("revise", event_loop_edge, ["execute_tool", END])


graph = builder.compile()
print(graph.get_graph().draw_mermaid())
graph.get_graph().draw_mermaid_png(output_file_path="flow.png")

if __name__ == "__main__":
    print("Starting Executing Reflexion Agent")
    main()
    response = graph.invoke(
        {
            "messages": HumanMessage(
                content="Write about AO powered cyber security promlem domain. list the startps That do that and  raise capita"
            )
        }
    )
    lastMessage: AIMessage = response["messages"][-1]
    print(type(lastMessage))
    print(f"Answer: \n {ReviseAnswer.model_validate_json(lastMessage.content)}")
