import httpx
import asyncio
import xml.etree.ElementTree as ET
from typing import List, Optional
from app.config import get_settings
from app.schemas.paper import PaperSearchResult
from app.models.paper import PaperSource

settings = get_settings()


class PubMedService:
    def __init__(self):
        self.base_url = settings.pubmed_base_url
        self.rate_limit = settings.pubmed_rate_limit

    async def search(self, query: str, max_results: int = 20) -> List[PaperSearchResult]:
        """Search PubMed for papers matching the query."""
        # Step 1: Search for IDs
        pmids = await self._search_ids(query, max_results)
        if not pmids:
            return []

        # Step 2: Fetch details for those IDs
        papers = await self._fetch_details(pmids)
        return papers

    async def _search_ids(self, query: str, max_results: int) -> List[str]:
        """Search PubMed and return PMIDs."""
        search_url = f"{self.base_url}/esearch.fcgi"
        params = {
            "db": "pubmed",
            "term": query,
            "retmax": max_results,
            "retmode": "json",
            "sort": "relevance"
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(search_url, params=params, timeout=30.0)
            response.raise_for_status()
            data = response.json()

        return data.get("esearchresult", {}).get("idlist", [])

    async def _fetch_details(self, pmids: List[str]) -> List[PaperSearchResult]:
        """Fetch paper details for given PMIDs."""
        if not pmids:
            return []

        fetch_url = f"{self.base_url}/efetch.fcgi"
        params = {
            "db": "pubmed",
            "id": ",".join(pmids),
            "retmode": "xml"
        }

        async with httpx.AsyncClient() as client:
            await asyncio.sleep(self.rate_limit)  # Rate limiting
            response = await client.get(fetch_url, params=params, timeout=60.0)
            response.raise_for_status()

        return self._parse_xml_response(response.text)

    def _parse_xml_response(self, xml_text: str) -> List[PaperSearchResult]:
        """Parse PubMed XML response into PaperSearchResult objects."""
        papers = []
        root = ET.fromstring(xml_text)

        for article in root.findall(".//PubmedArticle"):
            try:
                paper = self._parse_article(article)
                if paper:
                    papers.append(paper)
            except Exception:
                continue

        return papers

    def _parse_article(self, article: ET.Element) -> Optional[PaperSearchResult]:
        """Parse a single PubMed article element."""
        medline = article.find(".//MedlineCitation")
        if medline is None:
            return None

        pmid_elem = medline.find(".//PMID")
        pmid = pmid_elem.text if pmid_elem is not None else None
        if not pmid:
            return None

        article_elem = medline.find(".//Article")
        if article_elem is None:
            return None

        # Title
        title_elem = article_elem.find(".//ArticleTitle")
        title = title_elem.text if title_elem is not None else "Untitled"

        # Authors
        authors = []
        author_list = article_elem.find(".//AuthorList")
        if author_list is not None:
            for author in author_list.findall(".//Author"):
                lastname = author.find("LastName")
                forename = author.find("ForeName")
                if lastname is not None:
                    name = lastname.text
                    if forename is not None:
                        name = f"{forename.text} {name}"
                    authors.append(name)

        # Abstract
        abstract = None
        abstract_elem = article_elem.find(".//Abstract")
        if abstract_elem is not None:
            abstract_texts = []
            for text in abstract_elem.findall(".//AbstractText"):
                if text.text:
                    label = text.get("Label", "")
                    if label:
                        abstract_texts.append(f"{label}: {text.text}")
                    else:
                        abstract_texts.append(text.text)
            abstract = " ".join(abstract_texts)

        # Publication date
        pub_date = None
        pub_date_elem = article_elem.find(".//PubDate")
        if pub_date_elem is not None:
            year = pub_date_elem.find("Year")
            month = pub_date_elem.find("Month")
            if year is not None:
                pub_date = year.text
                if month is not None:
                    pub_date = f"{month.text} {pub_date}"

        # DOI
        doi = None
        for id_elem in article.findall(".//ArticleId"):
            if id_elem.get("IdType") == "doi":
                doi = id_elem.text
                break

        return PaperSearchResult(
            source=PaperSource.PUBMED,
            external_id=pmid,
            title=title,
            authors=authors,
            abstract=abstract,
            publication_date=pub_date,
            doi=doi,
            url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
            pdf_url=None  # PubMed doesn't directly provide PDFs
        )
