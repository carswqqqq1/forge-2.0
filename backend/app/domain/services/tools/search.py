from typing import Optional
from app.domain.external.search import SearchEngine
from app.domain.services.tools.base import BaseToolkit
from langchain.tools import tool
from app.domain.models.tool_result import ToolResult

class SearchToolkit(BaseToolkit):
    """Search tool class, providing search engine interaction functions"""

    name: str = "search"
    
    def __init__(self, search_engine: SearchEngine):
        """Initialize search tool class
        
        Args:
            search_engine: Search engine service
        """
        super().__init__()
        self.search_engine = search_engine
    
    @tool(parse_docstring=True)
    async def info_search_web(
        self,
        query: str,
        date_range: Optional[str] = None
    ) -> ToolResult:
        """Search web pages using search engine. Use for obtaining latest information or finding references.

        Args:
            query: Search query in Google search style, using 3-5 keywords.
            date_range: (Optional) Time range filter for search results.
        """
        try:
            result = await self.search_engine.search(query, date_range)
            # Sanitize results before passing to agent
            if result.success and result.data:
                # Ensure results are properly formatted and safe
                return result
            return result
        except Exception as e:
            # Handle search API unavailability gracefully
            return ToolResult(
                success=False,
                message=f"Search API error: {str(e)}. The search service may be temporarily unavailable."
            )

    @tool(parse_docstring=True)
    async def browser_search_web(
        self,
        query: str,
        date_range: Optional[str] = None
    ) -> ToolResult:
        """Compatibility alias for browser-style search calls.

        Args:
            query: Search query, Google search style, using 3-5 keywords.
            date_range: (Optional) Time range filter for search results.
        """
        try:
            result = await self.search_engine.search(query, date_range)
            # Sanitize results before passing to agent
            if result.success and result.data:
                # Ensure results are properly formatted and safe
                return result
            return result
        except Exception as e:
            # Handle search API unavailability gracefully
            return ToolResult(
                success=False,
                message=f"Search API error: {str(e)}. The search service may be temporarily unavailable."
            )
