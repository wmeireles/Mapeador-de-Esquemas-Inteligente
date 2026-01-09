"""
Phase 3: The Matching Agent
AI-powered semantic mapping between legacy and modern schemas.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pydantic import BaseModel
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from extractor import SchemaExtractor, SchemaEmbedder, TableInfo, ColumnInfo


class MappingResult(BaseModel):
    """Pydantic model for mapping results."""
    legacy_table: str
    legacy_column: str
    modern_table: str
    modern_column: str
    confidence_score: float
    transformation_logic: str
    reasoning: str


@dataclass
class SchemaMapping:
    """Complete schema mapping result."""
    table_mappings: List[MappingResult]
    unmapped_items: List[str]


class IntelligentMapper:
    """AI-powered schema mapper using semantic similarity and LLM verification."""
    
    def __init__(self, google_api_key: str):
        self.llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=google_api_key, temperature=0.1)
        self.embedder = SchemaEmbedder(google_api_key)
        self._load_vectorstore()
        self._setup_prompts()
    
    def _load_vectorstore(self) -> None:
        """Load existing vector store."""
        try:
            from langchain_chroma import Chroma
            from langchain_google_genai import GoogleGenerativeAIEmbeddings
            
            self.embedder.vectorstore = Chroma(
                persist_directory="./chroma_db",
                embedding_function=self.embedder.embeddings,
                collection_name="modern_schema"
            )
        except Exception as e:
            print(f"Warning: Could not load vector store: {e}")
    
    def _setup_prompts(self) -> None:
        """Setup LLM prompts for mapping verification."""
        self.mapping_prompt = PromptTemplate(
            input_variables=["legacy_item", "modern_candidates", "context"],
            template="""
You are a database schema mapping expert. Analyze the legacy database item and determine the best mapping to modern schema.

Legacy Item: {legacy_item}
Modern Candidates: {modern_candidates}
Context: {context}

Provide your analysis in JSON format:
{{
    "best_match": "modern_table.modern_column",
    "confidence": 0.85,
    "transformation_logic": "Direct mapping with no transformation needed",
    "reasoning": "Both represent customer full name with same data type"
}}

Consider:
1. Semantic meaning (e.g., 'c_nom' likely means 'customer name')
2. Data types compatibility
3. Business context (e.g., 'dt_nasc' = birth date)
4. Common abbreviations in legacy systems

Response (JSON only):
"""
        )
        
        self.mapping_chain = LLMChain(llm=self.llm, prompt=self.mapping_prompt)
    
    def _find_candidates(self, legacy_item: str, k: int = 5) -> List[Dict]:
        """Find candidate matches using vector similarity."""
        if not self.embedder.vectorstore:
            return []
        
        # Create search query with context
        search_query = f"database column field {legacy_item}"
        return self.embedder.find_similar(search_query, k=k)
    
    def _verify_mapping(self, legacy_item: str, candidates: List[Dict]) -> Optional[MappingResult]:
        """Use LLM to verify and select best mapping."""
        if not candidates:
            return None
        
        # Format candidates for LLM
        candidate_text = "\n".join([
            f"- {c['metadata'].get('table_name', 'unknown')}.{c['metadata'].get('column_name', 'unknown')} "
            f"({c['metadata'].get('data_type', 'unknown')}) - Score: {c['score']:.3f}"
            for c in candidates[:3]  # Top 3 candidates
        ])
        
        context = "Legacy system uses Portuguese abbreviations and obscure naming conventions."
        
        try:
            response = self.mapping_chain.run(
                legacy_item=legacy_item,
                modern_candidates=candidate_text,
                context=context
            )
            
            # Parse JSON response
            mapping_data = json.loads(response.strip())
            
            # Extract table and column from best_match
            if "." in mapping_data["best_match"]:
                modern_table, modern_column = mapping_data["best_match"].split(".", 1)
            else:
                return None
            
            # Parse legacy item
            if "." in legacy_item:
                legacy_table, legacy_column = legacy_item.split(".", 1)
            else:
                legacy_table, legacy_column = "unknown", legacy_item
            
            return MappingResult(
                legacy_table=legacy_table,
                legacy_column=legacy_column,
                modern_table=modern_table,
                modern_column=modern_column,
                confidence_score=float(mapping_data["confidence"]),
                transformation_logic=mapping_data["transformation_logic"],
                reasoning=mapping_data["reasoning"]
            )
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Error parsing LLM response for {legacy_item}: {e}")
            return None
    
    def map_schema(self, legacy_db_path: str) -> SchemaMapping:
        """Map entire legacy schema to modern schema."""
        # Extract legacy schema
        legacy_extractor = SchemaExtractor(legacy_db_path)
        legacy_tables = legacy_extractor.extract_schema()
        
        mappings = []
        unmapped = []
        
        print("Starting schema mapping...")
        
        for table in legacy_tables:
            print(f"Mapping table: {table.name}")
            
            for column in table.columns:
                legacy_item = f"{table.name}.{column.name}"
                print(f"  Mapping column: {legacy_item}")
                
                # Find candidates
                candidates = self._find_candidates(legacy_item)
                
                if not candidates:
                    unmapped.append(legacy_item)
                    continue
                
                # Verify mapping with LLM
                mapping = self._verify_mapping(legacy_item, candidates)
                
                if mapping and mapping.confidence_score > 0.5:
                    mappings.append(mapping)
                    print(f"    Mapped to: {mapping.modern_table}.{mapping.modern_column} "
                          f"(confidence: {mapping.confidence_score:.2f})")
                else:
                    unmapped.append(legacy_item)
                    print(f"    No confident mapping found")
        
        return SchemaMapping(table_mappings=mappings, unmapped_items=unmapped)
    
    def generate_sql_script(self, mappings: List[MappingResult]) -> str:
        """Generate SQL INSERT scripts based on mappings."""
        # Group mappings by target table
        table_mappings = {}
        for mapping in mappings:
            if mapping.modern_table not in table_mappings:
                table_mappings[mapping.modern_table] = []
            table_mappings[mapping.modern_table].append(mapping)
        
        sql_scripts = []
        
        for modern_table, table_mappings_list in table_mappings.items():
            # Build column lists
            modern_columns = [m.modern_column for m in table_mappings_list]
            legacy_columns = [f"{m.legacy_table}.{m.legacy_column}" for m in table_mappings_list]
            
            # Generate INSERT script
            script = f"""
-- Mapping for {modern_table}
INSERT INTO {modern_table} ({', '.join(modern_columns)})
SELECT {', '.join(legacy_columns)}
FROM {table_mappings_list[0].legacy_table};
"""
            sql_scripts.append(script)
        
        return "\n".join(sql_scripts)


def main() -> None:
    """Test the mapping functionality."""
    import os
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Please set GOOGLE_API_KEY environment variable")
        return
    
    mapper = IntelligentMapper(api_key)
    result = mapper.map_schema("legacy.db")
    
    print("\nMapping Results:")
    print(f"Successfully mapped: {len(result.table_mappings)} items")
    print(f"Unmapped items: {len(result.unmapped_items)}")
    
    if result.table_mappings:
        print("\nSuccessful Mappings:")
        for mapping in result.table_mappings:
            print(f"  {mapping.legacy_table}.{mapping.legacy_column} -> "
                  f"{mapping.modern_table}.{mapping.modern_column} "
                  f"({mapping.confidence_score:.2f})")
    
    if result.unmapped_items:
        print("\nUnmapped Items:")
        for item in result.unmapped_items:
            print(f"  {item}")


if __name__ == "__main__":
    main()