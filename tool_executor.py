from dotenv import load_dotenv
from langchain_core.tools import StructuredTool
from langchain_tavily import TavilySearch

load_dotenv()

tavily_tool = TavilySearch(max_results=5, topic="general")


def run_queries(searchList: list[str], **kwargs):
    """Run the generated queries."""
    results = tavily_tool.batch([query for query in searchList])
    return results
