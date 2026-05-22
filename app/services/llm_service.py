from langchain_anthropic import ChatAnthropic
from langchain_core.callbacks import AsyncCallbackHandler
from langchain_core.messages import HumanMessage, SystemMessage
from app.core.config import settings
from app.core.logging import logger
from typing import AsyncGenerator




class StreamingHandler(AsyncCallbackHandler):
    """Handle streaming tokens from Claude"""

    def __init__(self, on_token):
        self.on_token = on_token

    async def on_llm_new_token(self, token: str, **kwargs):
        """Called for each new token"""
        await self.on_token(token)

class LLMService:
    """LLM client using LangChain ChatAnthropic for LangGraph integration"""

    def __init__(self):
        self.client = ChatAnthropic(
            model="claude-sonnet-4-6",
            api_key=settings.anthropic_api_key,
            temperature=0.7,
        )
        self.model = "claude-sonnet-4-6"

    def get_client(self):
        """Return LangChain ChatAnthropic client"""
        return self.client

    def get_model(self):
        """Return model name"""
        return self.model

    async def generate(self, prompt: str, system: str = ""):
        """Generate response from Claude (non-streaming)"""
        import time

        messages = [HumanMessage(content=prompt)]
        if system:
            messages.insert(0, SystemMessage(content=system))

        try:
            logger.info(f"LLM: Calling Claude with prompt length {len(prompt)}")
            start_time = time.time()

            response = await self.client.ainvoke(messages)

            elapsed = time.time() - start_time
            logger.info(f"LLM: API call completed in {elapsed:.2f}s")
            logger.debug(f"LLM response type: {type(response)}")
            logger.debug(f"LLM response: {response}")

            if response is None:
                logger.error("LLM returned None")
                return ""

            # Handle different response types
            if hasattr(response, 'content'):
                content = response.content
            else:
                content = str(response)

            logger.debug(f"Extracted content: {content[:200] if content else 'empty'}")
            return content
        except Exception as e:
            logger.error(f"Error calling LLM: {e}", exc_info=True)
            raise

    async def generate_stream(
        self, prompt: str, system: str = ""
    ) -> AsyncGenerator[str, None]:
        """Generate response from Claude with token streaming"""
        messages = [HumanMessage(content=prompt)]
        if system:
            messages.insert(0, SystemMessage(content=system))

        async for chunk in self.client.astream(messages):
            if chunk.content:
                yield chunk.content

    async def generate_json(self, prompt: str, system: str = ""):
        """Generate JSON response from Claude"""
        import json

        full_response = await self.generate(prompt, system)
        try:
            return json.loads(full_response)
        except json.JSONDecodeError:
            # Fallback: try to extract JSON from response
            import re

            json_match = re.search(r"\{.*\}", full_response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {"raw": full_response}

llm_service = LLMService()
