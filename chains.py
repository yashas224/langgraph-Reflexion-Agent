import datetime

from dotenv import load_dotenv
from langchain.messages import HumanMessage, SystemMessage
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
)
from langchain_openai import ChatOpenAI

from schemas import AnswerQuestion, ReviseAnswer

load_dotenv()


system_prompt = SystemMessagePromptTemplate.from_template("""
        You are an expert researcher.
        Current time: {time}

        1. {first_instruction}
        2. Critique your answer.
        3. Suggest search queries.
        """)

actor_prompt_template = ChatPromptTemplate.from_messages(
    [
        system_prompt,
        MessagesPlaceholder(variable_name="messages"),
        SystemMessage(
            content="Answer the user's question above using the required format."
        ),
    ]
).partial(
    time=lambda: datetime.datetime.now().isoformat(),
)

revise_instructions = """Revise your previous answer using the new information.
    - You should use the previous critique to add important information to your answer.
        - You MUST include numerical citations in your revised answer to ensure it can be verified.
        - Add a "References" section to the bottom of your answer (which does not count towards the word limit). In form of:
            - [1] https://example.com
            - [2] https://example.com
    - You should use the previous critique to remove superfluous information from your answer and make SURE it is not more than 250 words.
"""

respond_instruction = "Provide a detailed ~250 word answer."

llm = ChatOpenAI(model="gpt-5.5", temperature=0)
respond_llm = llm.with_structured_output(AnswerQuestion)
rrevise_llm = llm.with_structured_output(ReviseAnswer)


responder_chain = (
    actor_prompt_template.partial(first_instruction=respond_instruction) | respond_llm
)

revisor_chain = (
    actor_prompt_template.partial(first_instruction=revise_instructions) | rrevise_llm
)
