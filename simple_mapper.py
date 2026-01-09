"""
Simplified Schema Mapper - Works without API calls for demonstration
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
import json
from extractor import SchemaExtractor, TableInfo, ColumnInfo


@dataclass
class SimpleMapping:
    """Simple mapping result without AI verification."""
    legacy_table: str
    legacy_column: str
    modern_table: str
    modern_column: str
    confidence_score: float
    reasoning: str


class SimpleMapper:
    """Rule-based schema mapper for demonstration."""
    
    def __init__(self):
        # Simple mapping rules based on common patterns
        self.column_mappings = {
            'c_nom': 'full_name',
            'c_email': 'email_address', 
            'dt_nasc': 'birth_date',
            'tel_cel': 'phone_number',
            'end_rua': 'street_address',
            'end_cep': 'postal_code',
            'dt_vnd': 'order_date',
            'vl_tot': 'total_amount',
            'st_vnd': 'order_status',
            'nm_prod': 'product_name',
            'desc_prod': 'product_description',
            'preco_unit': 'unit_price',
            'qtd_est': 'stock_quantity'
        }
        
        self.table_mappings = {
            'tb_cli_reg': 'customers',
            'tb_vendas_hdr': 'orders',
            'tb_prod_cat': 'products'
        }
    
    def map_schema(self, legacy_db_path: str) -> List[SimpleMapping]:
        """Map legacy schema using simple rules."""
        legacy_extractor = SchemaExtractor(legacy_db_path)
        legacy_tables = legacy_extractor.extract_schema()
        
        mappings = []
        
        for table in legacy_tables:
            modern_table = self.table_mappings.get(table.name, table.name)
            
            for column in table.columns:
                modern_column = self.column_mappings.get(column.name, column.name)
                
                # Calculate confidence based on exact match
                confidence = 0.9 if column.name in self.column_mappings else 0.3
                
                reasoning = f"Mapped '{column.name}' to '{modern_column}' based on naming patterns"
                
                mapping = SimpleMapping(
                    legacy_table=table.name,
                    legacy_column=column.name,
                    modern_table=modern_table,
                    modern_column=modern_column,
                    confidence_score=confidence,
                    reasoning=reasoning
                )
                mappings.append(mapping)
        
        return mappings
    
    def generate_sql_script(self, mappings: List[SimpleMapping]) -> str:
        """Generate SQL INSERT scripts."""
        table_mappings = {}
        for mapping in mappings:
            if mapping.modern_table not in table_mappings:
                table_mappings[mapping.modern_table] = []
            table_mappings[mapping.modern_table].append(mapping)
        
        sql_scripts = []
        
        for modern_table, table_mappings_list in table_mappings.items():
            modern_columns = [m.modern_column for m in table_mappings_list]
            legacy_columns = [f"{m.legacy_table}.{m.legacy_column}" for m in table_mappings_list]
            
            script = f"""
-- Mapping for {modern_table}
INSERT INTO {modern_table} ({', '.join(modern_columns)})
SELECT {', '.join(legacy_columns)}
FROM {table_mappings_list[0].legacy_table};
"""
            sql_scripts.append(script)
        
        return "\n".join(sql_scripts)


def main():
    """Test the simple mapper."""
    mapper = SimpleMapper()
    mappings = mapper.map_schema("legacy.db")
    
    print("\\nMapping Results:")
    print(f"Total mappings: {len(mappings)}")
    
    print("\\nMappings:")
    for mapping in mappings:
        print(f"  {mapping.legacy_table}.{mapping.legacy_column} -> "
              f"{mapping.modern_table}.{mapping.modern_column} "
              f"({mapping.confidence_score:.2f})")
    
    print("\\nGenerated SQL:")
    sql = mapper.generate_sql_script(mappings)
    print(sql)


if __name__ == "__main__":
    main()