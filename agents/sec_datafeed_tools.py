from agno.agent import Agent
from agno.embedder.fastembed import FastEmbedEmbedder
from agno.knowledge.text import TextKnowledgeBase
from agno.vectordb.pgvector import PgVector, SearchType
from agno.tools import Toolkit,tool
from sec_edgar_downloader import Downloader
import yfinance as yf
from typing import Optional
from db.session import db_url

class SECFilingTools(Toolkit):
    name = "SEC Filing Tools"
    description = "Tools for fetching and analyzing SEC filings"
    
    def __init__(self, **kwargs):
        tools = []
        tools.append(self.fetch_and_store_filings)
        tools.append(self.search_filings)
        super().__init__(name="sec_tools", tools=tools, **kwargs)
        self.dl = Downloader("MyCompanyName", "my.email@domain.com")
        self.db_url = db_url
        self.vector_db = PgVector(
            table_name="sec_filings",
            db_url=self.db_url,
            search_type=SearchType.hybrid,
            embedder=FastEmbedEmbedder(dimensions=1536)
        )
        self.knowledge_base = None
      
    def fetch_and_store_filings(self, ticker: str, filing_type: str = "10-K", limit: int = 3):
           
        try:
            # Download filings
            self.dl.get(filing_type, ticker, limit=limit)
            
            # Create and load knowledge base
            self.knowledge_base = TextKnowledgeBase(
                path=f"sec-edgar-filings/{ticker}/{filing_type}",
                vector_db=self.vector_db
            )
            self.knowledge_base.load(upsert=True)
            return f"Successfully stored {filing_type} filings for {ticker}"
        except Exception as e:
            return f"Error processing filings: {str(e)}"

    
    def search_filings(self, query: str, limit: int = 5):
        """Search stored SEC filings"""
        try:
            if not self.knowledge_base:
                return "No filings loaded yet. Please fetch filings first."
            results = self.vector_db.search(query, limit=limit)
            return results
        except Exception as e:
            return f"Error searching filings: {str(e)}"