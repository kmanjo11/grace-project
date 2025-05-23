"""
Research Service for Grace
This module implements a research service that integrates with SSRN and QuantConnect
to enhance Grace's knowledge through automated research gathering.
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import aiohttp
from bs4 import BeautifulSoup

from src.memory_system import MemorySystem

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("grace_research")


class ResearchService:
    """Service for gathering and processing research from SSRN and QuantConnect."""

    def __init__(self, memory_system: MemorySystem, interpreter=None):
        """
        Initialize the research service.

        Args:
            memory_system: Memory system for storing research findings
            interpreter: OpenInterpreter instance for web scraping
        """
        self.memory_system = memory_system
        self.interpreter = interpreter
        self.research_sources = {
            "ssrn": "https://www.ssrn.com/index.cfm/en/finplanrn/",
            "quantconnect": "https://www.quantconnect.com/research",
            "trading": "https://www.tradingview.com/ideas/",
            "defi": "https://defillama.com/protocols",
        }

    async def natural_research(self, topic: str, context: Optional[str] = None) -> None:
        """
        Let OI naturally explore and learn about a topic, following interesting leads.
        This is more like how a human would research - reading, connecting ideas, and
        going down relevant paths.

        Args:
            topic: Main research topic
            context: Optional context about why we're researching this
        """
        prompt = f"I'd like to learn about {topic}. {f'Context: {context}' if context else ''}\n\nFeel free to:\n- Visit relevant research sites and trading platforms\n- Follow interesting connections you find\n- Look for practical examples and case studies\n- Connect different concepts and ideas\n\nAs you learn, share your findings in a natural way that I can understand and use in conversations."

        try:
            findings = await self.interpreter.chat(prompt)
            # Store as conversational knowledge
            await self.memory_system.store(
                {
                    "type": "research_insight",
                    "topic": topic,
                    "context": context,
                    "findings": findings,
                    "timestamp": datetime.now().isoformat(),
                },
                tags=["research", "insight", topic],
            )
        except Exception as e:
            logger.error(f"Error in natural research: {str(e)}")

    async def structured_research(
        self, source: str, topic: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Systematic research gathering with structured data format.
        Good for collecting specific metrics, papers, or strategies.

        Args:
            source: Which source to research from
            topic: Optional topic filter
        """
        prompt = f"""
        Research {topic if topic else 'trading strategies'} on {source}.
        For each relevant item, collect:
        1. Title, URL, and summary
        2. For papers: authors, publication date
        3. For strategies: type, performance metrics
        4. Relevant topics and tags
        
        Return as structured data I can process.
        """

        try:
            results = await self.interpreter.chat(prompt)
            # Store as structured data
            await self.memory_system.store(
                results, tags=["research", source, "structured"]
            )
            return results
        except Exception as e:
            logger.error(f"Error in structured research: {str(e)}")
            return []

    async def passive_research(self) -> None:
        """
        Periodically check sources for new and interesting findings.
        This runs in the background to keep knowledge fresh.
        """
        while True:
            try:
                # Check each source for new content
                for source, url in self.research_sources.items():
                    prompt = f"""
                    Visit {url} and look for any new or interesting developments in the last 24 hours.
                    Focus on significant updates, trending topics, or important changes.
                    """

                    findings = await self.interpreter.chat(prompt)
                    if findings:
                        await self.memory_system.store(
                            {
                                "type": "passive_research",
                                "source": source,
                                "findings": findings,
                                "timestamp": datetime.now().isoformat(),
                            },
                            tags=["research", source, "passive"],
                        )

                # Wait for next check (e.g., every 24 hours)
                await asyncio.sleep(24 * 60 * 60)
            except Exception as e:
                logger.error(f"Error in passive research: {str(e)}")
                await asyncio.sleep(60 * 60)  # Wait an hour before retrying

    async def suggest_relevant_research(self, context: str) -> List[Dict[str, Any]]:
        """Find relevant research based on conversation context."""
        return await self.memory_system.search(
            query=context, tags=["research"], n_results=5
        )

    async def _fetch_ssrn(self, topic: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch research from SSRN using OpenInterpreter."""
        search_url = f"{self.ssrn_base_url}"
        if topic:
            search_url += f"?search={topic}"

        # Use OpenInterpreter to read and analyze the page
        analysis_prompt = f"""
        Visit {search_url} and:
        1. Look for the search box (usually at top of page)
        2. Enter the search term: {topic if topic else 'algorithmic trading'}
        3. Click the search button or press enter
        4. Wait for results to load
        5. For each research paper in the results:
           - Find the title (usually a clickable link)
           - Find the authors (usually below title)
           - Click to view full details if needed
           - Extract the abstract/summary
           - Get the paper's URL
           - Find the publication date

        Return the data as a list of JSON objects in this format:
        [
            {{
                "title": "paper title",
                "authors": ["author1", "author2"],
                "summary": "paper abstract",
                "url": "full paper url",
                "date": "YYYY-MM-DD",
                "topics": ["relevant", "topic", "tags"]
            }}
        ]
        """

        try:
            # This will use OI's capabilities to navigate and extract data
            results = await self.interpreter.chat(analysis_prompt)
            if isinstance(results, str):
                import json

                results = json.loads(results)
            return results
        except Exception as e:
            logger.error(f"Error fetching from SSRN: {str(e)}")
            return []

    async def _fetch_quantconnect(
        self, topic: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Fetch research from QuantConnect using OpenInterpreter."""
        search_url = f"{self.quantconnect_base_url}"
        if topic:
            search_url += f"?q={topic}"

        # Use OpenInterpreter to read and analyze the page
        analysis_prompt = f"""
        Visit {search_url} and:
        1. Find the strategy search/filter section
        2. Enter or select {topic if topic else 'algorithmic trading'}
        3. Apply the filter/search
        4. For each trading strategy in results:
           - Get the strategy name/title
           - Identify the strategy type (e.g., mean reversion, momentum)
           - Find and extract the strategy description
           - Get the strategy's URL
           - Look for performance metrics like:
             * Sharpe ratio
             * Returns
             * Win rate
             * Drawdown

        Return the data as a list of JSON objects in this format:
        [
            {{
                "title": "strategy name",
                "type": "strategy type",
                "description": "full description",
                "url": "strategy url",
                "performance": {{
                    "sharpe_ratio": number,
                    "returns": number,
                    "win_rate": number
                }},
                "topics": ["relevant", "topic", "tags"]
            }}
        ]
        """

        try:
            # This will use OI's capabilities to navigate and extract data
            results = await self.interpreter.chat(analysis_prompt)
            if isinstance(results, str):
                import json

                results = json.loads(results)
            return results
        except Exception as e:
            logger.error(f"Error fetching from QuantConnect: {str(e)}")
            return []

    def _validate_finding(self, finding: Dict[str, Any]) -> bool:
        """Validate research finding has required fields."""
        required_fields = ["title", "summary", "url"]
        valid = all(field in finding for field in required_fields)
        if not valid:
            logger.warning(
                f"Invalid research finding: missing required fields {[f for f in required_fields if f not in finding]}"
            )
        return valid

    def process_task(self, task_content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a task from the agent framework.

        Args:
            task_content: Task content and parameters

        Returns:
            Dict[str, Any]: Task result
        """
        task_type = task_content.get("type")

        if task_type == "natural_research":
            topic = task_content.get("topic")
            context = task_content.get("context")

            if not topic:
                return {"status": "error", "message": "Research topic is required"}

            # Since natural_research is async, we can't directly await it here
            # Instead, we'll start the task and return immediately
            try:
                asyncio.create_task(self.natural_research(topic, context))
                return {
                    "status": "success",
                    "message": f"Research on '{topic}' started in background",
                    "topic": topic,
                }
            except Exception as e:
                logger.error(f"Error starting natural research: {str(e)}")
                return {
                    "status": "error",
                    "message": f"Error starting research: {str(e)}",
                }

        elif task_type == "structured_research":
            source = task_content.get("source")
            topic = task_content.get("topic")

            if not source:
                return {"status": "error", "message": "Research source is required"}

            # Since structured_research is async, we can't directly await it here
            try:
                asyncio.create_task(self.structured_research(source, topic))
                return {
                    "status": "success",
                    "message": f"Structured research from '{source}' started in background",
                    "source": source,
                    "topic": topic,
                }
            except Exception as e:
                logger.error(f"Error starting structured research: {str(e)}")
                return {
                    "status": "error",
                    "message": f"Error starting research: {str(e)}",
                }

        elif task_type == "suggest_relevant_research":
            context = task_content.get("context")

            if not context:
                return {
                    "status": "error",
                    "message": "Context is required for research suggestions",
                }

            try:
                suggestions = self.suggest_relevant_research(context)
                return {"status": "success", "suggestions": suggestions}
            except Exception as e:
                logger.error(f"Error suggesting relevant research: {str(e)}")
                return {
                    "status": "error",
                    "message": f"Error suggesting research: {str(e)}",
                }

        elif task_type == "get_community_pulse":
            token = task_content.get("token")
            timeframe = task_content.get("timeframe", "24h")

            if not token:
                return {
                    "status": "error",
                    "message": "Token symbol is required for community pulse",
                }

            try:
                # In a real implementation, this would fetch social media sentiment,
                # trading activity, and community discussions about the token
                # For now, we'll return a placeholder response
                return {
                    "status": "success",
                    "token": token,
                    "timeframe": timeframe,
                    "sentiment": "neutral",
                    "activity": "moderate",
                    "trending_topics": [
                        "price action",
                        "new developments",
                        "market conditions",
                    ],
                    "summary": f"Community sentiment for {token} is currently neutral with moderate activity.",
                }
            except Exception as e:
                logger.error(f"Error getting community pulse: {str(e)}")
                return {
                    "status": "error",
                    "message": f"Error getting community pulse: {str(e)}",
                }

        return {"status": "error", "message": f"Unknown task type: {task_type}"}
