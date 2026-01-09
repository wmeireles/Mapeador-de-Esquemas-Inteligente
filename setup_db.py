"""
Phase 1: Mock Data Setup
Creates legacy.db and modern.db with sample schemas for testing.
"""

import sqlite3
from pathlib import Path
from typing import List, Tuple


def create_legacy_db() -> None:
    """Create legacy database with Portuguese/obscure naming conventions."""
    conn = sqlite3.connect("legacy.db")
    cursor = conn.cursor()
    
    # Legacy tables with Portuguese abbreviations
    legacy_tables = [
        """
        CREATE TABLE tb_cli_reg (
            id_cli INTEGER PRIMARY KEY,
            c_nom TEXT NOT NULL,
            c_email TEXT,
            dt_nasc DATE,
            tel_cel TEXT,
            end_rua TEXT,
            end_cep TEXT
        )
        """,
        """
        CREATE TABLE tb_vendas_hdr (
            id_vnd INTEGER PRIMARY KEY,
            id_cli INTEGER,
            dt_vnd DATE NOT NULL,
            vl_tot DECIMAL(10,2),
            st_vnd TEXT,
            FOREIGN KEY (id_cli) REFERENCES tb_cli_reg(id_cli)
        )
        """,
        """
        CREATE TABLE tb_prod_cat (
            id_prod INTEGER PRIMARY KEY,
            nm_prod TEXT NOT NULL,
            desc_prod TEXT,
            preco_unit DECIMAL(8,2),
            qtd_est INTEGER
        )
        """
    ]
    
    for table_sql in legacy_tables:
        cursor.execute(table_sql)
    
    # Insert sample data
    sample_data = [
        "INSERT INTO tb_cli_reg VALUES (1, 'João Silva', 'joao@email.com', '1985-03-15', '11999887766', 'Rua das Flores 123', '01234-567')",
        "INSERT INTO tb_vendas_hdr VALUES (1, 1, '2023-12-01', 299.99, 'CONF')",
        "INSERT INTO tb_prod_cat VALUES (1, 'Notebook Dell', 'Laptop para escritório', 2500.00, 10)"
    ]
    
    for data_sql in sample_data:
        cursor.execute(data_sql)
    
    conn.commit()
    conn.close()


def create_modern_db() -> None:
    """Create modern database with clean English naming conventions."""
    conn = sqlite3.connect("modern.db")
    cursor = conn.cursor()
    
    # Modern tables with clean English names
    modern_tables = [
        """
        CREATE TABLE customers (
            customer_id INTEGER PRIMARY KEY,
            full_name TEXT NOT NULL,
            email_address TEXT,
            birth_date DATE,
            phone_number TEXT,
            street_address TEXT,
            postal_code TEXT
        )
        """,
        """
        CREATE TABLE orders (
            order_id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            order_date DATE NOT NULL,
            total_amount DECIMAL(10,2),
            order_status TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        )
        """,
        """
        CREATE TABLE products (
            product_id INTEGER PRIMARY KEY,
            product_name TEXT NOT NULL,
            product_description TEXT,
            unit_price DECIMAL(8,2),
            stock_quantity INTEGER
        )
        """
    ]
    
    for table_sql in modern_tables:
        cursor.execute(table_sql)
    
    conn.commit()
    conn.close()


def main() -> None:
    """Initialize both databases."""
    print("Creating legacy.db...")
    create_legacy_db()
    
    print("Creating modern.db...")
    create_modern_db()
    
    print("✅ Databases created successfully!")
    print("- legacy.db: Portuguese/obscure naming")
    print("- modern.db: Clean English naming")


if __name__ == "__main__":
    main()