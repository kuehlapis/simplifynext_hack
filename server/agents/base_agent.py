from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from server.util.config import getConfig
from typing import Type, TypeVar
import yaml
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class BaseAgent:
    config = getConfig()
    API_KEY = config.get_gemini_api()

    def __init__(self):
        self.client = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=self.API_KEY,
        )

        self.prompt = ChatPromptTemplate.from_messages(
            [("system", "{system_prompt}"), ("human", "{input}")]
        )

    def get_system_prompt(self, agent_type: str) -> str:
        try:
            with open("server/agents/prompts/agent_prompts.yaml", "r") as f:
                data = yaml.safe_load(f)
                system_prompt = data["prompts"].get(agent_type, data["prompts"]["base"])
            return system_prompt
        except Exception as e:
            print(f"Error getting system prompt for {agent_type}: {e} ")

    def run(self, system_prompt: str, input: str, schema: Type[T]) -> T:
        """Run the agent with human input."""
        try:
            structured_client = self.client.with_structured_output(schema)

            chain = self.prompt | structured_client

            response: T = chain.invoke({"system_prompt": system_prompt, "input": input})

            return response
        except Exception as e:
            print(f"Error running client: {e}")
