import logging
from app.domain.services.flows.base import BaseFlow
from app.domain.models.message import Message
from typing import AsyncGenerator, Optional
from enum import Enum
from app.domain.models.event import (
    BaseEvent,
    PlanEvent,
    PlanStatus,
    MessageEvent,
    DoneEvent,
    TitleEvent,
    ErrorEvent,
)
from app.domain.models.plan import ExecutionStatus
from app.domain.services.agents.planner import PlannerAgent
from app.domain.services.agents.execution import ExecutionAgent
from app.domain.external.sandbox import Sandbox
from app.domain.external.browser import Browser
from app.domain.external.search import SearchEngine
from app.domain.repositories.agent_repository import AgentRepository
from app.domain.repositories.session_repository import SessionRepository
from app.domain.models.session import SessionStatus
from app.domain.services.tools.mcp import MCPToolkit
from app.domain.services.tools.shell import ShellToolkit
from app.domain.services.tools.browser import BrowserToolkit
from app.domain.services.tools.file import FileToolkit
from app.domain.services.tools.message import MessageToolkit
from app.domain.services.tools.search import SearchToolkit

logger = logging.getLogger(__name__)

class AgentStatus(str, Enum):
    IDLE = "idle"
    PLANNING = "planning"
    EXECUTING = "executing"
    SUMMARIZING = "summarizing"
    COMPLETED = "completed"
    UPDATING = "updating"

class PlanActFlow(BaseFlow):
    MAX_ITERATIONS = 1000  # Prevent infinite loops

    def __init__(
        self,
        agent_id: str,
        agent_repository: AgentRepository,
        session_id: str,
        session_repository: SessionRepository,
        sandbox: Sandbox,
        browser: Browser,
        mcp_tool: MCPToolkit,
        memory_brief: Optional[str] = None,
        search_engine: Optional[SearchEngine] = None,
    ):
        self._agent_id = agent_id
        self._repository = agent_repository
        self._session_id = session_id
        self._session_repository = session_repository
        self._memory_brief = memory_brief
        self.status = AgentStatus.IDLE
        self.plan = None
        self._iteration_count = 0

        tools = [
            ShellToolkit(sandbox),
            BrowserToolkit(browser),
            FileToolkit(sandbox),
            MessageToolkit(),
            mcp_tool
        ]
        
        # Only add search tool when search_engine is not None
        if search_engine:
            tools.append(SearchToolkit(search_engine))

        # Create planner and execution agents
        self.planner = PlannerAgent(
            agent_id=self._agent_id,
            agent_repository=self._repository,
            tools=tools,
            memory_brief=self._memory_brief,
        )
        logger.debug(f"Created planner agent for Agent {self._agent_id}")
            
        self.executor = ExecutionAgent(
            agent_id=self._agent_id,
            agent_repository=self._repository,
            tools=tools,
            memory_brief=self._memory_brief,
        )
        logger.debug(f"Created execution agent for Agent {self._agent_id}")

    async def run(self, message: Message) -> AsyncGenerator[BaseEvent, None]:

        # TODO: move to task runner
        session = await self._session_repository.find_by_id(self._session_id)
        if not session:
            raise ValueError(f"Session {self._session_id} not found")

        if session.status != SessionStatus.PENDING:
            logger.debug(f"Session {self._session_id} is not in PENDING status, rolling back")
            await self.executor.roll_back(message)
            await self.planner.roll_back(message)

        if session.status == SessionStatus.RUNNING:
            logger.debug(f"Session {self._session_id} is in RUNNING status")
            self.status = AgentStatus.PLANNING

        if session.status == SessionStatus.WAITING:
            logger.debug(f"Session {self._session_id} is in WAITING status")
            self.status = AgentStatus.EXECUTING

        await self._session_repository.update_status(self._session_id, SessionStatus.RUNNING)
        self.plan = session.get_last_plan()

        logger.info(f"Agent {self._agent_id} started processing message: {message.message[:50]}...")
        step = None
        self._iteration_count = 0
        while True:
            self._iteration_count += 1
            if self._iteration_count > self.MAX_ITERATIONS:
                logger.error(f"Agent {self._agent_id} exceeded maximum iterations ({self.MAX_ITERATIONS})")
                yield ErrorEvent(error=f"Task execution exceeded maximum iterations limit ({self.MAX_ITERATIONS})")
                self.status = AgentStatus.COMPLETED
                break
            if self.status == AgentStatus.IDLE:
                logger.info(f"Agent {self._agent_id} state changed from {AgentStatus.IDLE} to {AgentStatus.PLANNING}")
                self.status = AgentStatus.PLANNING
            elif self.status == AgentStatus.PLANNING:
                # Create plan
                logger.info(f"Agent {self._agent_id} started creating plan")
                plan_event = None
                try:
                    async for event in self.planner.create_plan(message):
                        if isinstance(event, PlanEvent) and event.status == PlanStatus.CREATED:
                            self.plan = event.plan
                            plan_event = event
                            logger.info(f"Agent {self._agent_id} created plan successfully with {len(event.plan.steps)} steps")
                            yield TitleEvent(title=event.plan.title)
                            yield MessageEvent(role="assistant", message=event.plan.message)
                        yield event
                except Exception as e:
                    logger.exception(f"Unhandled exception during plan creation")
                    yield ErrorEvent(error=f"Plan creation failed: {str(e)}")
                    self.status = AgentStatus.COMPLETED
                    continue

                logger.info(f"Agent {self._agent_id} state changed from {AgentStatus.PLANNING} to {AgentStatus.EXECUTING}")
                self.status = AgentStatus.EXECUTING
                if plan_event and len(plan_event.plan.steps) == 0:
                    logger.info(f"Agent {self._agent_id} created plan successfully with no steps")
                    self.status = AgentStatus.COMPLETED
                    
            elif self.status == AgentStatus.EXECUTING:
                # Execute plan
                self.plan.status = ExecutionStatus.RUNNING
                step = self.plan.get_next_step()
                if not step:
                    logger.info(f"Agent {self._agent_id} has no more steps, state changed from {AgentStatus.EXECUTING} to {AgentStatus.COMPLETED}")
                    self.status = AgentStatus.SUMMARIZING
                    continue
                # Execute step
                logger.info(f"Agent {self._agent_id} started executing step {step.id}: {step.description[:50]}...")
                try:
                    async for event in self.executor.execute_step(self.plan, step, message):
                        yield event
                except Exception as e:
                    logger.exception(f"Unhandled exception during step execution: {step.id}")
                    yield ErrorEvent(error=f"Step execution failed: {str(e)}")
                    step.status = ExecutionStatus.FAILED
                    step.error = str(e)
                    self.status = AgentStatus.SUMMARIZING
                    continue

                logger.info(f"Agent {self._agent_id} completed step {step.id}, state changed from {AgentStatus.EXECUTING} to {AgentStatus.UPDATING}")
                await self.executor.compact_memory()
                logger.debug(f"Agent {self._agent_id} compacted memory")
                self.status = AgentStatus.UPDATING
            elif self.status == AgentStatus.UPDATING:
                # Update plan
                logger.info(f"Agent {self._agent_id} started updating plan")
                try:
                    async for event in self.planner.update_plan(self.plan, step):
                        yield event
                except Exception as e:
                    logger.exception(f"Unhandled exception during plan update")
                    yield ErrorEvent(error=f"Plan update failed: {str(e)}")
                    self.status = AgentStatus.SUMMARIZING
                    continue

                logger.info(f"Agent {self._agent_id} plan update completed, state changed from {AgentStatus.UPDATING} to {AgentStatus.EXECUTING}")
                self.status = AgentStatus.EXECUTING
            elif self.status == AgentStatus.SUMMARIZING:
                # Conclusion
                logger.info(f"Agent {self._agent_id} started summarizing")
                try:
                    async for event in self.executor.summarize():
                        yield event
                except Exception as e:
                    logger.exception(f"Unhandled exception during summarization")
                    yield ErrorEvent(error=f"Summarization failed: {str(e)}")

                logger.info(f"Agent {self._agent_id} summarizing completed, state changed from {AgentStatus.SUMMARIZING} to {AgentStatus.COMPLETED}")
                self.status = AgentStatus.COMPLETED
            elif self.status == AgentStatus.COMPLETED:
                self.plan.status = ExecutionStatus.COMPLETED
                logger.info(f"Agent {self._agent_id} plan has been completed")
                yield PlanEvent(status=PlanStatus.COMPLETED, plan=self.plan)
                self.status = AgentStatus.IDLE
                break
        yield DoneEvent()
        
        logger.info(f"Agent {self._agent_id} message processing completed")
    
    def is_done(self) -> bool:
        return self.status == AgentStatus.IDLE
