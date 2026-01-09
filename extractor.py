"""
Phase 2: Schema Extraction & Embedding
Extracts database schemas and creates embeddings for semantic matching.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from sqlalchemy import create_engine, MetaData, inspect
from sqlalchemy.engine import Engine
import chromadb
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document


@dataclass
class ColumnInfo:
    """Column metadata information."""
    name: str
    data_type: str
    nullable: bool
    primary_key: bool
    foreign_key: Optional[str] = None


@dataclass
class TableInfo:
    """Table metadata information."""
    name: str
    columns: List[ColumnInfo]
    
    def to_description(self) -> str:
        """Convert table info to natural language description."""
        col_descriptions = []
        for col in self.columns:
            desc = f"{col.name} ({col.data_type})"
            if col.primary_key:
                desc += " [PRIMARY KEY]"
            if col.foreign_key:
                desc += f" [FOREIGN KEY -> {col.foreign_key}]"
            col_descriptions.append(desc)
        
        return f"Table: {self.name}\nColumns: {', '.join(col_descriptions)}"


class SchemaExtractor:
    """Extracts schema information from databases."""
    
    def __init__(self, db_path: str):
        self.engine = create_engine(f"sqlite:///{db_path}")
        self.inspector = inspect(self.engine)
    
    def extract_schema(self) -> List[TableInfo]:
        """Extract all tables and their column information."""
        tables = []
        
        for table_name in self.inspector.get_table_names():
            columns = []
            
            # Get column information
            for col in self.inspector.get_columns(table_name):
                column_info = ColumnInfo(
                    name=col['name'],
                    data_type=str(col['type']),
                    nullable=col['nullable'],
                    primary_key=col.get('primary_key', False)
                )
                columns.append(column_info)
            
            # Get foreign key information
            for fk in self.inspector.get_foreign_keys(table_name):
                for col_name in fk['constrained_columns']:
                    for col in columns:
                        if col.name == col_name:
                            col.foreign_key = f"{fk['referred_table']}.{fk['referred_columns'][0]}"
            
            tables.append(TableInfo(name=table_name, columns=columns))
        
        return tables


class SchemaEmbedder:
    """Creates and manages embeddings for schema information."""
    
    def __init__(self, google_api_key: str):
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=google_api_key)
        self.vectorstore: Optional[Chroma] = None
    
    def create_embeddings(self, tables: List[TableInfo], collection_name: str = "modern_schema") -> None:
        """Create embeddings for table and column descriptions."""
        documents = []
        
        # Create documents for tables
        for table in tables:
            # Table-level document
            table_doc = Document(
                page_content=table.to_description(),
                metadata={"type": "table", "name": table.name}
            )
            documents.append(table_doc)
            
            # Column-level documents
            for col in table.columns:
                col_doc = Document(
                    page_content=f"Column: {col.name} in table {table.name} - Type: {col.data_type}",
                    metadata={
                        "type": "column",
                        "table_name": table.name,
                        "column_name": col.name,
                        "data_type": col.data_type
                    }
                )
                documents.append(col_doc)
        
        # Create vector store
        self.vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            collection_name=collection_name,
            persist_directory="./chroma_db"
        )
        self.vectorstore.persist()
    
    def find_similar(self, query: str, k: int = 3) -> List[Dict]:
        """Find similar schema elements."""
        if not self.vectorstore:
            raise ValueError("Vector store not initialized. Call create_embeddings first.")
        
        results = self.vectorstore.similarity_search_with_score(query, k=k)
        return [
            {
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": score
            }
            for doc, score in results
        ]


def main() -> None:
    """Extract schemas and create embeddings."""
    import os
    from dotenv import load_dotenv
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Check for Google API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Please set GOOGLE_API_KEY environment variable")
        return
    
    print("Extracting legacy schema...")
    legacy_extractor = SchemaExtractor("legacy.db")
    legacy_tables = legacy_extractor.extract_schema()
    
    print("Extracting modern schema...")
    modern_extractor = SchemaExtractor("modern.db")
    modern_tables = modern_extractor.extract_schema()
    
    print("Creating embeddings for modern schema...")
    embedder = SchemaEmbedder(api_key)
    embedder.create_embeddings(modern_tables)
    
    print("Schema extraction and embedding creation completed!")
    print(f"Legacy tables: {[t.name for t in legacy_tables]}")
    print(f"Modern tables: {[t.name for t in modern_tables]}")


if __name__ == "__main__":
    main()