from typing import Type

import instructor
from app.settings import AgentConfig
from openai import OpenAI
from pydantic import BaseModel


class BaseAgent:

    def __init__(self, config: AgentConfig, system_prompt: str, response_model: Type[BaseModel]):

        self.llm_model = config.MODEL
        self.temperature = config.TEMPERATURE
        self._system_prompt = system_prompt
        self.response_schema = response_model

        self.client = instructor.patch(OpenAI(api_key=config.TOKEN.get_secret_value()))

    @property
    def system_prompt(self) -> str:
        return self._system_prompt

    @system_prompt.setter
    def system_prompt(self, new_system_prompt: str) -> None:
        self._system_prompt = new_system_prompt

    def run(self, user_input: str) -> BaseModel:
        messages = [
            {"role": "system", "content": self._system_prompt},
            {"role": "user", "content": user_input},
        ]

        conversation_result = self.client.chat.completions.create(
            model=self.llm_model, response_model=self.response_schema, messages=messages, temperature=self.temperature
        )
        return conversation_result
