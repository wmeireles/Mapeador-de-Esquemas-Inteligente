"""
Configuration Manager for Schema Mapper
"""

import json
import os
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class DatabaseConfig:
    """Database configuration."""
    name: str
    path: str
    type: str = "sqlite"
    description: str = ""


@dataclass
class MappingRule:
    """Custom mapping rule."""
    pattern: str
    replacement: str
    description: str = ""
    created_at: str = ""


@dataclass
class ProjectConfig:
    """Project configuration."""
    name: str
    description: str
    legacy_db: DatabaseConfig
    modern_db: DatabaseConfig
    custom_rules: List[MappingRule]
    created_at: str
    last_modified: str


class ConfigManager:
    """Manages project configurations."""
    
    def __init__(self, config_dir: str = "configs"):
        self.config_dir = config_dir
        os.makedirs(config_dir, exist_ok=True)
    
    def save_project(self, config: ProjectConfig) -> str:
        """Save project configuration."""
        config.last_modified = datetime.now().isoformat()
        
        filename = f"{config.name.replace(' ', '_').lower()}.json"
        filepath = os.path.join(self.config_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(asdict(config), f, indent=2)
        
        return filepath
    
    def load_project(self, filename: str) -> Optional[ProjectConfig]:
        """Load project configuration."""
        filepath = os.path.join(self.config_dir, filename)
        
        if not os.path.exists(filepath):
            return None
        
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        # Convert back to dataclasses
        legacy_db = DatabaseConfig(**data['legacy_db'])
        modern_db = DatabaseConfig(**data['modern_db'])
        
        custom_rules = [MappingRule(**rule) for rule in data['custom_rules']]
        
        return ProjectConfig(
            name=data['name'],
            description=data['description'],
            legacy_db=legacy_db,
            modern_db=modern_db,
            custom_rules=custom_rules,
            created_at=data['created_at'],
            last_modified=data['last_modified']
        )
    
    def list_projects(self) -> List[str]:
        """List all saved projects."""
        if not os.path.exists(self.config_dir):
            return []
        
        return [f for f in os.listdir(self.config_dir) if f.endswith('.json')]
    
    def delete_project(self, filename: str) -> bool:
        """Delete a project configuration."""
        filepath = os.path.join(self.config_dir, filename)
        
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        
        return False


class MappingExporter:
    """Export mappings in different formats."""
    
    @staticmethod
    def to_csv(mappings: List, filename: str) -> str:
        """Export mappings to CSV."""
        import pandas as pd
        
        data = []
        for mapping in mappings:
            data.append({
                'Legacy Table': mapping.legacy_table,
                'Legacy Column': mapping.legacy_column,
                'Modern Table': mapping.modern_table,
                'Modern Column': mapping.modern_column,
                'Confidence': mapping.confidence_score,
                'Reasoning': mapping.reasoning
            })
        
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        return filename
    
    @staticmethod
    def to_json(mappings: List, filename: str) -> str:
        """Export mappings to JSON."""
        data = []
        for mapping in mappings:
            data.append({
                'legacy_table': mapping.legacy_table,
                'legacy_column': mapping.legacy_column,
                'modern_table': mapping.modern_table,
                'modern_column': mapping.modern_column,
                'confidence_score': mapping.confidence_score,
                'reasoning': mapping.reasoning
            })
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        return filename
    
    @staticmethod
    def to_excel(mappings: List, filename: str) -> str:
        """Export mappings to Excel with multiple sheets."""
        import pandas as pd
        
        # Main mappings sheet
        main_data = []
        for mapping in mappings:
            main_data.append({
                'Legacy Table': mapping.legacy_table,
                'Legacy Column': mapping.legacy_column,
                'Modern Table': mapping.modern_table,
                'Modern Column': mapping.modern_column,
                'Confidence': mapping.confidence_score,
                'Reasoning': mapping.reasoning
            })
        
        # Summary sheet
        summary_data = {
            'Metric': ['Total Mappings', 'High Confidence (>0.8)', 'Medium Confidence (0.5-0.8)', 'Low Confidence (<0.5)'],
            'Count': [
                len(mappings),
                len([m for m in mappings if m.confidence_score > 0.8]),
                len([m for m in mappings if 0.5 <= m.confidence_score <= 0.8]),
                len([m for m in mappings if m.confidence_score < 0.5])
            ]
        }
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            pd.DataFrame(main_data).to_excel(writer, sheet_name='Mappings', index=False)
            pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
        
        return filename


def create_sample_config() -> ProjectConfig:
    """Create a sample project configuration."""
    legacy_db = DatabaseConfig(
        name="Legacy ERP",
        path="legacy.db",
        type="sqlite",
        description="Legacy ERP system with Portuguese naming conventions"
    )
    
    modern_db = DatabaseConfig(
        name="Modern Cloud DB",
        path="modern.db",
        type="sqlite",
        description="Modern cloud database with clean English naming"
    )
    
    custom_rules = [
        MappingRule(
            pattern="c_*",
            replacement="*_name",
            description="Map customer fields to name fields",
            created_at=datetime.now().isoformat()
        ),
        MappingRule(
            pattern="dt_*",
            replacement="*_date",
            description="Map date fields",
            created_at=datetime.now().isoformat()
        )
    ]
    
    return ProjectConfig(
        name="ERP Migration Project",
        description="Migration from legacy ERP to modern cloud system",
        legacy_db=legacy_db,
        modern_db=modern_db,
        custom_rules=custom_rules,
        created_at=datetime.now().isoformat(),
        last_modified=datetime.now().isoformat()
    )


if __name__ == "__main__":
    # Test the configuration manager
    config_manager = ConfigManager()
    
    # Create and save sample config
    sample_config = create_sample_config()
    filepath = config_manager.save_project(sample_config)
    print(f"Saved sample config to: {filepath}")
    
    # List projects
    projects = config_manager.list_projects()
    print(f"Available projects: {projects}")
    
    # Load project
    loaded_config = config_manager.load_project(projects[0])
    print(f"Loaded project: {loaded_config.name}")