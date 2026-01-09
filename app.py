"""
Phase 4: Human-in-the-loop UI
Streamlit interface for reviewing and approving schema mappings.
"""

import streamlit as st
import pandas as pd
import os
from typing import List, Dict
import json
from mapper import IntelligentMapper, MappingResult, SchemaMapping
from extractor import SchemaExtractor


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'mappings' not in st.session_state:
        st.session_state.mappings = []
    if 'approved_mappings' not in st.session_state:
        st.session_state.approved_mappings = []
    if 'mapping_complete' not in st.session_state:
        st.session_state.mapping_complete = False


def load_mappings() -> SchemaMapping:
    """Load or generate schema mappings."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        st.error("❌ Please set GOOGLE_API_KEY environment variable")
        st.stop()
    
    with st.spinner("🔍 Analyzing schemas and generating mappings..."):
        mapper = IntelligentMapper(api_key)
        return mapper.map_schema("legacy.db")


def display_schema_overview():
    """Display overview of both schemas."""
    st.subheader("📊 Schema Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Legacy Database (legacy.db)**")
        legacy_extractor = SchemaExtractor("legacy.db")
        legacy_tables = legacy_extractor.extract_schema()
        
        for table in legacy_tables:
            with st.expander(f"Table: {table.name}"):
                for col in table.columns:
                    st.write(f"• {col.name} ({col.data_type})")
    
    with col2:
        st.write("**Modern Database (modern.db)**")
        modern_extractor = SchemaExtractor("modern.db")
        modern_tables = modern_extractor.extract_schema()
        
        for table in modern_tables:
            with st.expander(f"Table: {table.name}"):
                for col in table.columns:
                    st.write(f"• {col.name} ({col.data_type})")


def display_mapping_interface(mappings: List[MappingResult]):
    """Display interface for reviewing and editing mappings."""
    st.subheader("🔗 Schema Mappings Review")
    
    if not mappings:
        st.warning("No mappings found. Please check your databases and try again.")
        return
    
    # Create DataFrame for easier display
    mapping_data = []
    for i, mapping in enumerate(mappings):
        mapping_data.append({
            'ID': i,
            'Legacy': f"{mapping.legacy_table}.{mapping.legacy_column}",
            'Modern': f"{mapping.modern_table}.{mapping.modern_column}",
            'Confidence': f"{mapping.confidence_score:.2f}",
            'Transformation': mapping.transformation_logic,
            'Reasoning': mapping.reasoning
        })
    
    df = pd.DataFrame(mapping_data)
    
    # Display mappings with approval interface
    for i, mapping in enumerate(mappings):
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 3, 2, 2])
            
            with col1:
                st.write(f"**Legacy:** {mapping.legacy_table}.{mapping.legacy_column}")
            
            with col2:
                # Allow editing of modern mapping
                modern_options = get_modern_columns()
                current_modern = f"{mapping.modern_table}.{mapping.modern_column}"
                
                selected_modern = st.selectbox(
                    "Modern Column:",
                    options=modern_options,
                    index=modern_options.index(current_modern) if current_modern in modern_options else 0,
                    key=f"modern_{i}"
                )
            
            with col3:
                confidence_color = "🟢" if mapping.confidence_score > 0.8 else "🟡" if mapping.confidence_score > 0.6 else "🔴"
                st.write(f"{confidence_color} {mapping.confidence_score:.2f}")
            
            with col4:
                if st.button(f"✅ Approve", key=f"approve_{i}"):
                    # Update mapping if modified
                    if selected_modern != current_modern:
                        table, column = selected_modern.split(".", 1)
                        mapping.modern_table = table
                        mapping.modern_column = column
                    
                    st.session_state.approved_mappings.append(mapping)
                    st.success(f"Approved mapping for {mapping.legacy_table}.{mapping.legacy_column}")
            
            # Show reasoning in expander
            with st.expander(f"Reasoning for {mapping.legacy_table}.{mapping.legacy_column}"):
                st.write(f"**Transformation:** {mapping.transformation_logic}")
                st.write(f"**Reasoning:** {mapping.reasoning}")
            
            st.divider()


def get_modern_columns() -> List[str]:
    """Get all available modern database columns."""
    modern_extractor = SchemaExtractor("modern.db")
    modern_tables = modern_extractor.extract_schema()
    
    columns = []
    for table in modern_tables:
        for col in table.columns:
            columns.append(f"{table.name}.{col.name}")
    
    return sorted(columns)


def generate_final_script():
    """Generate and display final SQL migration script."""
    if not st.session_state.approved_mappings:
        st.warning("No approved mappings to generate script.")
        return
    
    st.subheader("📝 Generated Migration Script")
    
    api_key = os.getenv("GOOGLE_API_KEY")
    mapper = IntelligentMapper(api_key)
    sql_script = mapper.generate_sql_script(st.session_state.approved_mappings)
    
    st.code(sql_script, language="sql")
    
    # Download button
    st.download_button(
        label="📥 Download Migration Script",
        data=sql_script,
        file_name="migration_script.sql",
        mime="text/sql"
    )
    
    # Summary
    st.success(f"✅ Migration script generated for {len(st.session_state.approved_mappings)} approved mappings!")


def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="Intelligent Schema Mapper",
        page_icon="🗄️",
        layout="wide"
    )
    
    st.title("🗄️ Intelligent Schema Mapper")
    st.markdown("AI-powered database schema mapping for legacy system migrations")
    
    initialize_session_state()
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Choose a page:",
        ["Schema Overview", "Generate Mappings", "Review Mappings", "Generate Script"]
    )
    
    if page == "Schema Overview":
        display_schema_overview()
    
    elif page == "Generate Mappings":
        st.subheader("🤖 Generate AI Mappings")
        
        if st.button("🚀 Start Mapping Process"):
            # Check if databases exist
            if not os.path.exists("legacy.db") or not os.path.exists("modern.db"):
                st.error("❌ Database files not found. Please run setup_db.py first.")
                return
            
            # Load mappings
            schema_mapping = load_mappings()
            st.session_state.mappings = schema_mapping.table_mappings
            st.session_state.mapping_complete = True
            
            st.success(f"✅ Generated {len(schema_mapping.table_mappings)} mappings!")
            
            if schema_mapping.unmapped_items:
                st.warning(f"⚠️ {len(schema_mapping.unmapped_items)} items could not be mapped:")
                for item in schema_mapping.unmapped_items:
                    st.write(f"• {item}")
    
    elif page == "Review Mappings":
        if not st.session_state.mapping_complete:
            st.info("Please generate mappings first.")
        else:
            display_mapping_interface(st.session_state.mappings)
            
            # Show approved mappings summary
            if st.session_state.approved_mappings:
                st.subheader("✅ Approved Mappings")
                approved_df = pd.DataFrame([
                    {
                        'Legacy': f"{m.legacy_table}.{m.legacy_column}",
                        'Modern': f"{m.modern_table}.{m.modern_column}",
                        'Confidence': f"{m.confidence_score:.2f}"
                    }
                    for m in st.session_state.approved_mappings
                ])
                st.dataframe(approved_df, use_container_width=True)
    
    elif page == "Generate Script":
        generate_final_script()
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Status:**")
    st.sidebar.write(f"Mappings Generated: {'✅' if st.session_state.mapping_complete else '❌'}")
    st.sidebar.write(f"Approved: {len(st.session_state.approved_mappings)}")


if __name__ == "__main__":
    main()