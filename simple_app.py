"""
Simplified Streamlit App - Works without API calls
"""

import streamlit as st
import pandas as pd
from typing import List
from simple_mapper import SimpleMapper, SimpleMapping
from extractor import SchemaExtractor


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'mappings' not in st.session_state:
        st.session_state.mappings = []
    if 'approved_mappings' not in st.session_state:
        st.session_state.approved_mappings = []


def display_schema_overview():
    """Display overview of both schemas."""
    st.subheader("Schema Overview")
    
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


def display_mapping_interface(mappings: List[SimpleMapping]):
    """Display interface for reviewing mappings."""
    st.subheader("Schema Mappings Review")
    
    if not mappings:
        st.warning("No mappings found.")
        return
    
    # Display mappings with approval interface
    for i, mapping in enumerate(mappings):
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 3, 2, 2])
            
            with col1:
                st.write(f"**Legacy:** {mapping.legacy_table}.{mapping.legacy_column}")
            
            with col2:
                st.write(f"**Modern:** {mapping.modern_table}.{mapping.modern_column}")
            
            with col3:
                confidence_color = "🟢" if mapping.confidence_score > 0.8 else "🟡" if mapping.confidence_score > 0.6 else "🔴"
                st.write(f"{confidence_color} {mapping.confidence_score:.2f}")
            
            with col4:
                if st.button(f"Approve", key=f"approve_{i}"):
                    if mapping not in st.session_state.approved_mappings:
                        st.session_state.approved_mappings.append(mapping)
                        st.success(f"Approved!")
            
            # Show reasoning
            with st.expander(f"Details for {mapping.legacy_table}.{mapping.legacy_column}"):
                st.write(f"**Reasoning:** {mapping.reasoning}")
            
            st.divider()


def generate_final_script():
    """Generate and display final SQL migration script."""
    if not st.session_state.approved_mappings:
        st.warning("No approved mappings to generate script.")
        return
    
    st.subheader("Generated Migration Script")
    
    mapper = SimpleMapper()
    sql_script = mapper.generate_sql_script(st.session_state.approved_mappings)
    
    st.code(sql_script, language="sql")
    
    # Download button
    st.download_button(
        label="Download Migration Script",
        data=sql_script,
        file_name="migration_script.sql",
        mime="text/sql"
    )
    
    st.success(f"Migration script generated for {len(st.session_state.approved_mappings)} approved mappings!")


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
        st.subheader("Generate Mappings")
        
        if st.button("Start Mapping Process"):
            mapper = SimpleMapper()
            mappings = mapper.map_schema("legacy.db")
            st.session_state.mappings = mappings
            
            st.success(f"Generated {len(mappings)} mappings!")
            
            # Show summary
            df = pd.DataFrame([
                {
                    'Legacy': f"{m.legacy_table}.{m.legacy_column}",
                    'Modern': f"{m.modern_table}.{m.modern_column}",
                    'Confidence': f"{m.confidence_score:.2f}"
                }
                for m in mappings
            ])
            st.dataframe(df, use_container_width=True)
    
    elif page == "Review Mappings":
        if not st.session_state.mappings:
            st.info("Please generate mappings first.")
        else:
            display_mapping_interface(st.session_state.mappings)
            
            # Show approved mappings summary
            if st.session_state.approved_mappings:
                st.subheader("Approved Mappings")
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
    st.sidebar.write(f"Mappings Generated: {'✅' if st.session_state.mappings else '❌'}")
    st.sidebar.write(f"Approved: {len(st.session_state.approved_mappings)}")


if __name__ == "__main__":
    main()