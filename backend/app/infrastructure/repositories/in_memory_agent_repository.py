from datetime import datetime, UTC
from typing import Optional

from app.domain.models.agent import Agent
from app.domain.models.memory import Memory
from app.domain.repositories.agent_repository import AgentRepository


class InMemoryAgentRepository(AgentRepository):
    """In-memory agent repository for standalone development."""

    def __init__(self):
        self._agents: dict[str, Agent] = {}

    async def save(self, agent: Agent) -> None:
        self._agents[agent.id] = agent.model_copy(deep=True)

    async def find_by_id(self, agent_id: str) -> Optional[Agent]:
        agent = self._agents.get(agent_id)
        return agent.model_copy(deep=True) if agent else None

    async def add_memory(self, agent_id: str, name: str, memory: Memory) -> None:
        agent = self._agents.get(agent_id)
        if not agent:
            raise ValueError(f"Agent {agent_id} not found")
        agent.memories[name] = memory.model_copy(deep=True)
        agent.updated_at = datetime.now(UTC)

    async def get_memory(self, agent_id: str, name: str) -> Memory:
        agent = self._agents.get(agent_id)
        if not agent:
            raise ValueError(f"Agent {agent_id} not found")
        memory = agent.memories.get(name, Memory(messages=[]))
        return memory.model_copy(deep=True)

    async def save_memory(self, agent_id: str, name: str, memory: Memory) -> None:
        await self.add_memory(agent_id, name, memory)
