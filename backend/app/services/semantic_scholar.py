import httpx
import asyncio
from typing import List, Optional
from app.config import get_settings
from app.schemas.paper import PaperSearchResult
from app.models.paper import PaperSource

settings = get_settings()


class SemanticScholarService:
    def __init__(self):
        self.base_url = settings.semantic_scholar_base_url
        self.api_key = settings.semantic_scholar_api_key

    def _get_headers(self) -> dict:
        headers = {}
        if self.api_key:
            headers["x-api-key"] = self.api_key
        return headers

    async def search(self, query: str, max_results: int = 20) -> List[PaperSearchResult]:
        """Search Semantic Scholar for papers matching the query."""
        search_url = f"{self.base_url}/paper/search"
        params = {
            "query": query,
            "limit": min(max_results, 100),  # API max is 100
            "fields": "paperId,title,authors,abstract,year,publicationDate,externalIds,url,openAccessPdf"
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(
                search_url,
                params=params,
                headers=self._get_headers(),
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()

        papers = []
        for item in data.get("data", []):
            paper = self._parse_paper(item)
            if paper:
                papers.append(paper)

        return papers

    def _parse_paper(self, data: dict) -> Optional[PaperSearchResult]:
        """Parse a Semantic Scholar paper response."""
        paper_id = data.get("paperId")
        title = data.get("title")

        if not paper_id or not title:
            return None

        # Authors
        authors = []
        for author in data.get("authors", []):
            name = author.get("name")
            if name:
                authors.append(name)

        # External IDs (DOI, etc.)
        external_ids = data.get("externalIds", {})
        doi = external_ids.get("DOI")

        # Publication date
        pub_date = data.get("publicationDate")
        if not pub_date:
            year = data.get("year")
            if year:
                pub_date = str(year)

        # PDF URL from openAccessPdf
        pdf_url = None
        open_access = data.get("openAccessPdf")
        if open_access:
            pdf_url = open_access.get("url")

        return PaperSearchResult(
            source=PaperSource.SEMANTIC_SCHOLAR,
            external_id=paper_id,
            title=title,
            authors=authors,
            abstract=data.get("abstract"),
            publication_date=pub_date,
            doi=doi,
            url=data.get("url") or f"https://www.semanticscholar.org/paper/{paper_id}",
            pdf_url=pdf_url
        )

    async def get_paper_details(self, paper_id: str) -> Optional[dict]:
        """Get detailed information about a specific paper."""
        url = f"{self.base_url}/paper/{paper_id}"
        params = {
            "fields": "paperId,title,authors,abstract,year,publicationDate,externalIds,url,openAccessPdf,citations,references,tldr"
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                params=params,
                headers=self._get_headers(),
                timeout=30.0
            )
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return response.json()

    async def get_related_papers(self, paper_id: str, limit: int = 10) -> List[PaperSearchResult]:
        """Get papers related to a given paper."""
        url = f"{self.base_url}/paper/{paper_id}/recommendations"
        params = {
            "limit": limit,
            "fields": "paperId,title,authors,abstract,year,publicationDate,externalIds,url,openAccessPdf"
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                params=params,
                headers=self._get_headers(),
                timeout=30.0
            )
            if response.status_code == 404:
                return []
            response.raise_for_status()
            data = response.json()

        papers = []
        for item in data.get("recommendedPapers", []):
            paper = self._parse_paper(item)
            if paper:
                papers.append(paper)

        return papers
