from agno.tools import Toolkit
from agno.knowledge.text import TextKnowledgeBase
from agno.embedder.fastembed import FastEmbedEmbedder
from agno.embedder.openai import OpenAIEmbedder
from agno.vectordb.pgvector import PgVector, SearchType
from agno.tools.knowledge import KnowledgeTools
from agno.document import TextDocument
import finnhub
import requests

class FinnhubFilingsTools(Toolkit):
    def __init__(self, api_key):
        self.api_key = api_key

        # Setup Finnhub client
        self.client = finnhub.Client(api_key=self.api_key)

        # Initialize vector database
        self.vector_db = PgVector(
            table_name="sec_filings",
            db_url=self.db_url,
            search_type=SearchType.hybrid,
            embedder=FastEmbedEmbedder(dimensions=1536)
        )

        # Initialize knowledge base
        self.knowledge_base = TextKnowledgeBase(
            
            vector_db=self.vector_db
        )

        # Initialize knowledge tools
        self.knowledge_tools = KnowledgeTools(
            knowledge=self.knowledge_base,
            think=True,
            search=True,
            analyze=True
        )

        # Initialize toolkit with tools
        super().__init__(
            tools=[
                self.fetch_filings,
                *self.knowledge_tools.tools
            ]
        )

    def fetch_filings(self, symbol: str):
        """Fetch recent SEC filings from Finnhub and store them in the knowledge base"""
        try:
            filings = self.client.filings(symbol=symbol)

            if not filings:
                return f"No filings found for {symbol}."

            count = 0
            for filing in filings[:5]: 
                url = filing.get("reportUrl") or filing.get("formUrl")
                if not url:
                    continue

                try:
                    response = requests.get(url)
                    if response.status_code != 200:
                        continue
                    text = response.text
                except Exception as e:
                    print(f"Error downloading filing: {str(e)}")
                    continue

                self.knowledge_base = TextKnowledgeBase(
                path=f"sec-edgar-filings/{symbol}",
                vector_db=self.vector_db
                )
                self.knowledge_base.load(upsert=True)
                count += 1

            return f"Successfully added {count} filings for {symbol} to the knowledge base."
        except Exception as e:
            return f"Error fetching filings: {str(e)}"