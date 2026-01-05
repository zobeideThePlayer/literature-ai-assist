from openai import AsyncOpenAI
from typing import List, Optional, AsyncGenerator
import json
from app.config import get_settings
from app.models.insight import InsightType

settings = get_settings()


# Prompt templates for different analysis tasks
PROMPTS = {
    "relevance": """You are a research assistant helping to evaluate the relevance of a scientific paper to a specific research question.

Research Question: {research_question}
Domain: {domain}

Paper Title: {title}
Abstract: {abstract}

Evaluate how relevant this paper is to the research question. Consider:
1. Direct relevance to the topic
2. Methodological relevance
3. Theoretical relevance
4. Potential for providing insights

Respond in JSON format:
{{
    "relevance_score": <float between 0 and 1>,
    "explanation": "<brief explanation of relevance>",
    "key_aspects": ["<relevant aspect 1>", "<relevant aspect 2>", ...]
}}""",

    "extract_findings": """You are a research assistant extracting key findings from a scientific paper.

Research Question: {research_question}
Domain: {domain}

Paper Title: {title}
Abstract: {abstract}

Extract the key findings from this paper. For each finding, provide:
1. The main claim or finding
2. The evidence supporting it
3. Any limitations mentioned

Respond in JSON format:
{{
    "key_findings": [
        {{
            "finding": "<main finding>",
            "evidence": "<supporting evidence>",
            "limitations": "<any limitations>"
        }}
    ],
    "methodology": "<brief description of methods used>",
    "sample_size": "<sample size if mentioned>",
    "reasoning": "<your step-by-step reasoning for identifying these findings>"
}}""",

    "cross_paper_analysis": """You are a research assistant synthesizing findings across multiple papers for a literature review.

Research Question: {research_question}
Domain: {domain}

Papers and their key findings:
{papers_summary}

Analyze these papers together and identify:
1. Common themes
2. Contradictory findings
3. Research gaps
4. Areas of consensus

For each insight, explain your reasoning step by step.

Respond in JSON format:
{{
    "themes": [
        {{
            "theme": "<identified theme>",
            "supporting_papers": ["<paper title 1>", "<paper title 2>"],
            "reasoning": "<how you identified this theme>"
        }}
    ],
    "contradictions": [
        {{
            "topic": "<topic of contradiction>",
            "positions": ["<position 1>", "<position 2>"],
            "papers": ["<paper 1>", "<paper 2>"],
            "reasoning": "<how these contradict>"
        }}
    ],
    "gaps": [
        {{
            "gap": "<identified research gap>",
            "reasoning": "<why this is a gap>"
        }}
    ],
    "consensus": [
        {{
            "finding": "<area of agreement>",
            "papers": ["<supporting papers>"],
            "strength": "<strong/moderate/weak>"
        }}
    ]
}}""",

    "generate_review": """You are an expert academic writer helping to create a literature review section for a peer-reviewed article.

Research Question: {research_question}
Domain: {domain}

Papers Analyzed:
{papers_summary}

Key Themes Identified:
{themes}

Research Gaps:
{gaps}

Areas of Consensus:
{consensus}

Contradictions Found:
{contradictions}

Write a comprehensive literature review section that:
1. Introduces the research question and its importance
2. Organizes findings thematically
3. Critically analyzes the literature
4. Identifies gaps and future directions
5. Maintains academic tone and style

The review should be suitable for inclusion in a peer-reviewed article. Include proper in-text citations using author-date format.

At the end, include a "Chain of Thought" section explaining how you organized and synthesized the literature.
"""
}


class LLMService:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.deepseek_api_key,
            base_url=settings.deepseek_base_url
        )
        self.model = settings.deepseek_model

    async def evaluate_relevance(
        self,
        title: str,
        abstract: str,
        research_question: str,
        domain: str
    ) -> dict:
        """Evaluate the relevance of a paper to the research question."""
        prompt = PROMPTS["relevance"].format(
            research_question=research_question,
            domain=domain,
            title=title,
            abstract=abstract or "No abstract available"
        )

        response = await self._complete(prompt)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {
                "relevance_score": 0.5,
                "explanation": response,
                "key_aspects": []
            }

    async def extract_findings(
        self,
        title: str,
        abstract: str,
        research_question: str,
        domain: str
    ) -> dict:
        """Extract key findings from a paper."""
        prompt = PROMPTS["extract_findings"].format(
            research_question=research_question,
            domain=domain,
            title=title,
            abstract=abstract or "No abstract available"
        )

        response = await self._complete(prompt)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {
                "key_findings": [],
                "methodology": "",
                "sample_size": "",
                "reasoning": response
            }

    async def analyze_papers(
        self,
        papers_summary: str,
        research_question: str,
        domain: str
    ) -> dict:
        """Perform cross-paper analysis to identify themes, gaps, etc."""
        prompt = PROMPTS["cross_paper_analysis"].format(
            research_question=research_question,
            domain=domain,
            papers_summary=papers_summary
        )

        response = await self._complete(prompt, max_tokens=4000)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {
                "themes": [],
                "contradictions": [],
                "gaps": [],
                "consensus": [],
                "raw_response": response
            }

    async def generate_review(
        self,
        research_question: str,
        domain: str,
        papers_summary: str,
        themes: str,
        gaps: str,
        consensus: str,
        contradictions: str
    ) -> str:
        """Generate a complete literature review section."""
        prompt = PROMPTS["generate_review"].format(
            research_question=research_question,
            domain=domain,
            papers_summary=papers_summary,
            themes=themes,
            gaps=gaps,
            consensus=consensus,
            contradictions=contradictions
        )

        return await self._complete(prompt, max_tokens=6000)

    async def generate_review_stream(
        self,
        research_question: str,
        domain: str,
        papers_summary: str,
        themes: str,
        gaps: str,
        consensus: str,
        contradictions: str
    ) -> AsyncGenerator[str, None]:
        """Generate a literature review with streaming output."""
        prompt = PROMPTS["generate_review"].format(
            research_question=research_question,
            domain=domain,
            papers_summary=papers_summary,
            themes=themes,
            gaps=gaps,
            consensus=consensus,
            contradictions=contradictions
        )

        async for chunk in self._stream(prompt, max_tokens=6000):
            yield chunk

    async def _complete(self, prompt: str, max_tokens: int = 2000) -> str:
        """Make a completion request to the LLM."""
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful research assistant specializing in academic literature analysis. Always respond in the requested format."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.3  # Lower temperature for more consistent analysis
        )
        return response.choices[0].message.content

    async def _stream(self, prompt: str, max_tokens: int = 2000) -> AsyncGenerator[str, None]:
        """Make a streaming completion request to the LLM."""
        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful research assistant specializing in academic literature analysis."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.3,
            stream=True
        )

        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
