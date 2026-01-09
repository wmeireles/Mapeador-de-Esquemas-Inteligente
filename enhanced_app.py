"""
Enhanced Schema Mapper with improved features
"""

import streamlit as st
import pandas as pd
import os
import json
from typing import List, Dict, Optional
from datetime import datetime
from simple_mapper import SimpleMapper, SimpleMapping
from extractor import SchemaExtractor
import sqlite3


class EnhancedMapper(SimpleMapper):
    """Enhanced mapper with additional features."""
    
    def __init__(self):
        super().__init__()
        self.mapping_history = []
    
    def analyze_data_types(self, legacy_db_path: str) -> Dict:
        """Analyze data types and suggest transformations."""
        conn = sqlite3.connect(legacy_db_path)
        cursor = conn.cursor()
        
        analysis = {}
        
        # Get sample data for analysis
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
            sample_data = cursor.fetchall()
            
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            analysis[table_name] = {
                'columns': columns,
                'sample_data': sample_data,
                'row_count': cursor.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
            }
        
        conn.close()
        return analysis
    
    def suggest_data_transformations(self, mapping: SimpleMapping, analysis: Dict) -> List[str]:
        """Suggest data transformations based on analysis."""
        suggestions = []
        
        # Check for common transformation patterns
        if 'dt_' in mapping.legacy_column or 'date' in mapping.legacy_column.lower():
            suggestions.append("Consider date format conversion (DD/MM/YYYY to YYYY-MM-DD)")
        
        if 'vl_' in mapping.legacy_column or 'preco' in mapping.legacy_column:
            suggestions.append("Check decimal precision and currency formatting")
        
        if 'tel_' in mapping.legacy_column or 'phone' in mapping.modern_column:
            suggestions.append("Standardize phone number format")
        
        if 'email' in mapping.legacy_column or 'email' in mapping.modern_column:
            suggestions.append("Validate email format and normalize case")
        
        return suggestions
    
    def export_mapping_report(self, mappings: List[SimpleMapping], analysis: Dict) -> str:
        """Generate detailed mapping report."""
        report = f"""
# Schema Mapping Report
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
- Total mappings: {len(mappings)}
- High confidence (>0.8): {len([m for m in mappings if m.confidence_score > 0.8])}
- Medium confidence (0.5-0.8): {len([m for m in mappings if 0.5 <= m.confidence_score <= 0.8])}
- Low confidence (<0.5): {len([m for m in mappings if m.confidence_score < 0.5])}

## Data Analysis
"""
        
        for table_name, data in analysis.items():
            report += f"\n### Table: {table_name}\n"
            report += f"- Row count: {data['row_count']}\n"
            report += f"- Columns: {len(data['columns'])}\n"
        
        report += "\n## Detailed Mappings\n"
        
        for mapping in mappings:
            report += f"\n### {mapping.legacy_table}.{mapping.legacy_column} → {mapping.modern_table}.{mapping.modern_column}\n"
            report += f"- Confidence: {mapping.confidence_score:.2f}\n"
            report += f"- Reasoning: {mapping.reasoning}\n"
            
            suggestions = self.suggest_data_transformations(mapping, analysis)
            if suggestions:
                report += "- Transformation suggestions:\n"
                for suggestion in suggestions:
                    report += f"  - {suggestion}\n"
        
        return report


def initialize_enhanced_session_state():
    """Initialize enhanced session state."""
    if 'mappings' not in st.session_state:
        st.session_state.mappings = []
    if 'approved_mappings' not in st.session_state:
        st.session_state.approved_mappings = []
    if 'analysis' not in st.session_state:
        st.session_state.analysis = {}
    if 'custom_rules' not in st.session_state:
        st.session_state.custom_rules = {}


def display_enhanced_overview():
    """Enhanced schema overview with statistics."""
    st.subheader("📊 Enhanced Schema Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Legacy Database Analysis**")
        legacy_extractor = SchemaExtractor("legacy.db")
        legacy_tables = legacy_extractor.extract_schema()
        
        # Statistics
        total_columns = sum(len(table.columns) for table in legacy_tables)
        st.metric("Tables", len(legacy_tables))
        st.metric("Total Columns", total_columns)
        
        # Table details
        for table in legacy_tables:
            with st.expander(f"📋 {table.name} ({len(table.columns)} columns)"):
                for col in table.columns:
                    pk_indicator = " 🔑" if col.primary_key else ""
                    fk_indicator = " 🔗" if col.foreign_key else ""
                    st.write(f"• {col.name} ({col.data_type}){pk_indicator}{fk_indicator}")
    
    with col2:
        st.write("**Modern Database Schema**")
        modern_extractor = SchemaExtractor("modern.db")
        modern_tables = modern_extractor.extract_schema()
        
        # Statistics
        total_columns = sum(len(table.columns) for table in modern_tables)
        st.metric("Tables", len(modern_tables))
        st.metric("Total Columns", total_columns)
        
        # Table details
        for table in modern_tables:
            with st.expander(f"📋 {table.name} ({len(table.columns)} columns)"):
                for col in table.columns:
                    pk_indicator = " 🔑" if col.primary_key else ""
                    fk_indicator = " 🔗" if col.foreign_key else ""
                    st.write(f"• {col.name} ({col.data_type}){pk_indicator}{fk_indicator}")


def display_custom_rules():
    """Interface for custom mapping rules."""
    st.subheader("⚙️ Custom Mapping Rules")
    
    st.write("Add custom rules to improve mapping accuracy:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        legacy_pattern = st.text_input("Legacy Pattern (e.g., 'c_*')")
        
    with col2:
        modern_pattern = st.text_input("Modern Pattern (e.g., '*_name')")
    
    if st.button("Add Rule"):
        if legacy_pattern and modern_pattern:
            st.session_state.custom_rules[legacy_pattern] = modern_pattern
            st.success(f"Added rule: {legacy_pattern} → {modern_pattern}")
    
    # Display existing rules
    if st.session_state.custom_rules:
        st.write("**Current Rules:**")
        for legacy, modern in st.session_state.custom_rules.items():
            col1, col2, col3 = st.columns([3, 3, 1])
            with col1:
                st.write(legacy)
            with col2:
                st.write(modern)
            with col3:
                if st.button("🗑️", key=f"del_{legacy}"):
                    del st.session_state.custom_rules[legacy]
                    st.rerun()


def display_enhanced_mappings(mappings: List[SimpleMapping]):
    """Enhanced mapping interface with filtering and sorting."""
    st.subheader("🔗 Enhanced Mapping Review")
    
    if not mappings:
        st.warning("No mappings found.")
        return
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        confidence_filter = st.selectbox(
            "Filter by Confidence",
            ["All", "High (>0.8)", "Medium (0.5-0.8)", "Low (<0.5)"]
        )
    
    with col2:
        table_filter = st.selectbox(
            "Filter by Table",
            ["All"] + list(set(m.legacy_table for m in mappings))
        )
    
    with col3:
        sort_by = st.selectbox(
            "Sort by",
            ["Confidence (High to Low)", "Confidence (Low to High)", "Table Name", "Column Name"]
        )
    
    # Apply filters
    filtered_mappings = mappings.copy()
    
    if confidence_filter == "High (>0.8)":
        filtered_mappings = [m for m in filtered_mappings if m.confidence_score > 0.8]
    elif confidence_filter == "Medium (0.5-0.8)":
        filtered_mappings = [m for m in filtered_mappings if 0.5 <= m.confidence_score <= 0.8]
    elif confidence_filter == "Low (<0.5)":
        filtered_mappings = [m for m in filtered_mappings if m.confidence_score < 0.5]
    
    if table_filter != "All":
        filtered_mappings = [m for m in filtered_mappings if m.legacy_table == table_filter]
    
    # Apply sorting
    if sort_by == "Confidence (High to Low)":
        filtered_mappings.sort(key=lambda x: x.confidence_score, reverse=True)
    elif sort_by == "Confidence (Low to High)":
        filtered_mappings.sort(key=lambda x: x.confidence_score)
    elif sort_by == "Table Name":
        filtered_mappings.sort(key=lambda x: x.legacy_table)
    elif sort_by == "Column Name":
        filtered_mappings.sort(key=lambda x: x.legacy_column)
    
    st.write(f"Showing {len(filtered_mappings)} of {len(mappings)} mappings")
    
    # Bulk actions
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Approve All High Confidence"):
            high_conf = [m for m in filtered_mappings if m.confidence_score > 0.8]
            st.session_state.approved_mappings.extend(high_conf)
            st.success(f"Approved {len(high_conf)} high confidence mappings")
    
    with col2:
        if st.button("🔄 Reset All Approvals"):
            st.session_state.approved_mappings = []
            st.success("Reset all approvals")
    
    # Display mappings
    for i, mapping in enumerate(filtered_mappings):
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 3, 2, 2])
            
            with col1:
                st.write(f"**{mapping.legacy_table}.{mapping.legacy_column}**")
            
            with col2:
                st.write(f"**{mapping.modern_table}.{mapping.modern_column}**")
            
            with col3:
                if mapping.confidence_score > 0.8:
                    st.success(f"🟢 {mapping.confidence_score:.2f}")
                elif mapping.confidence_score > 0.5:
                    st.warning(f"🟡 {mapping.confidence_score:.2f}")
                else:
                    st.error(f"🔴 {mapping.confidence_score:.2f}")
            
            with col4:
                is_approved = mapping in st.session_state.approved_mappings
                if st.button(
                    "✅ Approved" if is_approved else "Approve", 
                    key=f"approve_{i}",
                    disabled=is_approved
                ):
                    if not is_approved:
                        st.session_state.approved_mappings.append(mapping)
                        st.rerun()
            
            # Enhanced details
            with st.expander(f"Details: {mapping.legacy_table}.{mapping.legacy_column}"):
                st.write(f"**Reasoning:** {mapping.reasoning}")
                
                # Data transformation suggestions
                mapper = EnhancedMapper()
                suggestions = mapper.suggest_data_transformations(mapping, st.session_state.analysis)
                if suggestions:
                    st.write("**Transformation Suggestions:**")
                    for suggestion in suggestions:
                        st.write(f"• {suggestion}")
            
            st.divider()


def main():
    """Enhanced main application."""
    st.set_page_config(
        page_title="Enhanced Schema Mapper",
        page_icon="🗄️",
        layout="wide"
    )
    
    st.title("🗄️ Enhanced Intelligent Schema Mapper")
    st.markdown("Advanced AI-powered database schema mapping with enhanced features")
    
    initialize_enhanced_session_state()
    
    # Enhanced sidebar
    st.sidebar.title("🚀 Navigation")
    page = st.sidebar.radio(
        "Choose a page:",
        [
            "📊 Schema Overview", 
            "⚙️ Custom Rules",
            "🤖 Generate Mappings", 
            "🔗 Review Mappings", 
            "📝 Generate Script",
            "📋 Export Report"
        ]
    )
    
    if page == "📊 Schema Overview":
        display_enhanced_overview()
    
    elif page == "⚙️ Custom Rules":
        display_custom_rules()
    
    elif page == "🤖 Generate Mappings":
        st.subheader("🤖 Generate Enhanced Mappings")
        
        if st.button("🚀 Start Enhanced Mapping Process"):
            with st.spinner("Analyzing schemas and generating mappings..."):
                mapper = EnhancedMapper()
                
                # Apply custom rules
                for pattern, replacement in st.session_state.custom_rules.items():
                    # Simple pattern matching (can be enhanced)
                    if '*' in pattern:
                        base_pattern = pattern.replace('*', '')
                        for key in list(mapper.column_mappings.keys()):
                            if base_pattern in key:
                                mapper.column_mappings[key] = replacement.replace('*', key.replace(base_pattern, ''))
                
                mappings = mapper.map_schema("legacy.db")
                analysis = mapper.analyze_data_types("legacy.db")
                
                st.session_state.mappings = mappings
                st.session_state.analysis = analysis
            
            st.success(f"✅ Generated {len(mappings)} enhanced mappings!")
            
            # Show statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                high_conf = len([m for m in mappings if m.confidence_score > 0.8])
                st.metric("High Confidence", high_conf)
            with col2:
                med_conf = len([m for m in mappings if 0.5 <= m.confidence_score <= 0.8])
                st.metric("Medium Confidence", med_conf)
            with col3:
                low_conf = len([m for m in mappings if m.confidence_score < 0.5])
                st.metric("Low Confidence", low_conf)
    
    elif page == "🔗 Review Mappings":
        if not st.session_state.mappings:
            st.info("Please generate mappings first.")
        else:
            display_enhanced_mappings(st.session_state.mappings)
    
    elif page == "📝 Generate Script":
        if not st.session_state.approved_mappings:
            st.warning("No approved mappings to generate script.")
        else:
            st.subheader("📝 Enhanced Migration Script")
            
            mapper = EnhancedMapper()
            sql_script = mapper.generate_sql_script(st.session_state.approved_mappings)
            
            st.code(sql_script, language="sql")
            
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="📥 Download SQL Script",
                    data=sql_script,
                    file_name=f"migration_script_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql",
                    mime="text/sql"
                )
            
            with col2:
                # Generate validation script
                validation_script = f"""
-- Validation queries for migration
-- Run these after migration to verify data integrity

{chr(10).join([f"SELECT COUNT(*) as {mapping.modern_table}_count FROM {mapping.modern_table};" for mapping in st.session_state.approved_mappings[:3]])}
"""
                st.download_button(
                    label="📋 Download Validation Script",
                    data=validation_script,
                    file_name=f"validation_script_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql",
                    mime="text/sql"
                )
    
    elif page == "📋 Export Report":
        if not st.session_state.mappings:
            st.info("Please generate mappings first.")
        else:
            st.subheader("📋 Export Detailed Report")
            
            mapper = EnhancedMapper()
            report = mapper.export_mapping_report(st.session_state.mappings, st.session_state.analysis)
            
            st.markdown(report)
            
            st.download_button(
                label="📥 Download Report",
                data=report,
                file_name=f"mapping_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown"
            )
    
    # Enhanced footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("**📊 Status Dashboard**")
    st.sidebar.write(f"Mappings: {len(st.session_state.mappings)}")
    st.sidebar.write(f"Approved: {len(st.session_state.approved_mappings)}")
    st.sidebar.write(f"Custom Rules: {len(st.session_state.custom_rules)}")
    
    if st.session_state.mappings:
        approval_rate = len(st.session_state.approved_mappings) / len(st.session_state.mappings) * 100
        st.sidebar.progress(approval_rate / 100)
        st.sidebar.write(f"Approval Rate: {approval_rate:.1f}%")


if __name__ == "__main__":
    main()