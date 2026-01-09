"""
Data Quality Validator for Schema Mapping
"""

import sqlite3
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import re
from datetime import datetime


@dataclass
class QualityIssue:
    """Represents a data quality issue."""
    table: str
    column: str
    issue_type: str
    description: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    sample_values: List[str]
    count: int


@dataclass
class QualityReport:
    """Data quality assessment report."""
    database_name: str
    total_tables: int
    total_columns: int
    total_rows: int
    issues: List[QualityIssue]
    score: float  # 0-100
    generated_at: str


class DataQualityValidator:
    """Validates data quality and suggests improvements."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
    
    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()
    
    def validate_database(self) -> QualityReport:
        """Perform comprehensive data quality validation."""
        cursor = self.conn.cursor()
        
        # Get database metadata
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        total_tables = len(tables)
        total_columns = 0
        total_rows = 0
        issues = []
        
        for table in tables:
            # Get table info
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            total_columns += len(columns)
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            row_count = cursor.fetchone()[0]
            total_rows += row_count
            
            # Validate each column
            for col_info in columns:
                col_name = col_info[1]
                col_type = col_info[2]
                
                column_issues = self._validate_column(table, col_name, col_type)
                issues.extend(column_issues)
        
        # Calculate quality score
        score = self._calculate_quality_score(issues, total_columns)
        
        return QualityReport(
            database_name=self.db_path,
            total_tables=total_tables,
            total_columns=total_columns,
            total_rows=total_rows,
            issues=issues,
            score=score,
            generated_at=datetime.now().isoformat()
        )
    
    def _validate_column(self, table: str, column: str, col_type: str) -> List[QualityIssue]:
        """Validate a specific column."""
        issues = []
        cursor = self.conn.cursor()
        
        # Get sample data
        cursor.execute(f"SELECT {column} FROM {table} WHERE {column} IS NOT NULL LIMIT 100")
        sample_data = [row[0] for row in cursor.fetchall()]
        
        if not sample_data:
            return issues
        
        # Check for null values
        cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE {column} IS NULL")
        null_count = cursor.fetchone()[0]
        
        if null_count > 0:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            total_count = cursor.fetchone()[0]
            null_percentage = (null_count / total_count) * 100
            
            if null_percentage > 50:
                severity = 'critical'
            elif null_percentage > 20:
                severity = 'high'
            elif null_percentage > 5:
                severity = 'medium'
            else:
                severity = 'low'
            
            issues.append(QualityIssue(
                table=table,
                column=column,
                issue_type='null_values',
                description=f'{null_percentage:.1f}% null values',
                severity=severity,
                sample_values=[],
                count=null_count
            ))
        
        # Type-specific validations
        if 'email' in column.lower():
            issues.extend(self._validate_email_column(table, column, sample_data))
        
        if 'phone' in column.lower() or 'tel' in column.lower():
            issues.extend(self._validate_phone_column(table, column, sample_data))
        
        if 'date' in column.lower() or 'dt_' in column.lower():
            issues.extend(self._validate_date_column(table, column, sample_data))
        
        # Check for duplicates in potential unique columns
        if 'id' in column.lower() or 'email' in column.lower():
            issues.extend(self._check_duplicates(table, column))
        
        # Check data consistency
        issues.extend(self._check_data_consistency(table, column, sample_data))
        
        return issues
    
    def _validate_email_column(self, table: str, column: str, sample_data: List) -> List[QualityIssue]:
        """Validate email format."""
        issues = []
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        
        invalid_emails = []
        for email in sample_data:
            if email and not email_pattern.match(str(email)):
                invalid_emails.append(str(email))
        
        if invalid_emails:
            cursor = self.conn.cursor()
            cursor.execute(f"""
                SELECT COUNT(*) FROM {table} 
                WHERE {column} IS NOT NULL 
                AND {column} NOT LIKE '%@%.%'
            """)
            invalid_count = cursor.fetchone()[0]
            
            issues.append(QualityIssue(
                table=table,
                column=column,
                issue_type='invalid_email_format',
                description=f'Invalid email format detected',
                severity='medium',
                sample_values=invalid_emails[:5],
                count=invalid_count
            ))
        
        return issues
    
    def _validate_phone_column(self, table: str, column: str, sample_data: List) -> List[QualityIssue]:
        """Validate phone number format."""
        issues = []
        
        # Check for consistent formatting
        formats = set()
        for phone in sample_data:
            if phone:
                # Remove common separators and count digits
                digits_only = re.sub(r'[^\d]', '', str(phone))
                formats.add(len(digits_only))
        
        if len(formats) > 2:  # Too many different formats
            issues.append(QualityIssue(
                table=table,
                column=column,
                issue_type='inconsistent_phone_format',
                description=f'Multiple phone formats detected: {formats}',
                severity='medium',
                sample_values=[str(x) for x in sample_data[:5]],
                count=len(sample_data)
            ))
        
        return issues
    
    def _validate_date_column(self, table: str, column: str, sample_data: List) -> List[QualityIssue]:
        """Validate date format and values."""
        issues = []
        
        # Check for future dates where inappropriate
        future_dates = []
        for date_val in sample_data:
            if date_val:
                try:
                    # Try to parse as date
                    if isinstance(date_val, str):
                        parsed_date = pd.to_datetime(date_val)
                        if parsed_date > datetime.now():
                            future_dates.append(str(date_val))
                except:
                    pass
        
        if future_dates and 'birth' in column.lower():
            issues.append(QualityIssue(
                table=table,
                column=column,
                issue_type='future_birth_dates',
                description='Future birth dates detected',
                severity='high',
                sample_values=future_dates[:5],
                count=len(future_dates)
            ))
        
        return issues
    
    def _check_duplicates(self, table: str, column: str) -> List[QualityIssue]:
        """Check for duplicate values in unique columns."""
        issues = []
        cursor = self.conn.cursor()
        
        cursor.execute(f"""
            SELECT {column}, COUNT(*) as cnt 
            FROM {table} 
            WHERE {column} IS NOT NULL 
            GROUP BY {column} 
            HAVING COUNT(*) > 1
            LIMIT 10
        """)
        
        duplicates = cursor.fetchall()
        
        if duplicates:
            duplicate_values = [str(row[0]) for row in duplicates]
            total_duplicates = sum(row[1] - 1 for row in duplicates)  # Subtract 1 for original
            
            issues.append(QualityIssue(
                table=table,
                column=column,
                issue_type='duplicate_values',
                description=f'Duplicate values in potentially unique column',
                severity='high' if 'id' in column.lower() else 'medium',
                sample_values=duplicate_values[:5],
                count=total_duplicates
            ))
        
        return issues
    
    def _check_data_consistency(self, table: str, column: str, sample_data: List) -> List[QualityIssue]:
        """Check for data consistency issues."""
        issues = []
        
        # Check for mixed case in text fields
        if any(isinstance(x, str) for x in sample_data):
            text_values = [str(x) for x in sample_data if x]
            
            has_mixed_case = any(
                val != val.lower() and val != val.upper() and val != val.title()
                for val in text_values
            )
            
            if has_mixed_case and len(set(val.lower() for val in text_values)) < len(text_values) * 0.8:
                issues.append(QualityIssue(
                    table=table,
                    column=column,
                    issue_type='inconsistent_case',
                    description='Inconsistent text casing detected',
                    severity='low',
                    sample_values=text_values[:5],
                    count=len(text_values)
                ))
        
        return issues
    
    def _calculate_quality_score(self, issues: List[QualityIssue], total_columns: int) -> float:
        """Calculate overall data quality score (0-100)."""
        if not issues:
            return 100.0
        
        # Weight issues by severity
        severity_weights = {
            'low': 1,
            'medium': 3,
            'high': 7,
            'critical': 15
        }
        
        total_weight = sum(severity_weights[issue.severity] for issue in issues)
        max_possible_weight = total_columns * severity_weights['critical']
        
        # Calculate score (higher weight = lower score)
        score = max(0, 100 - (total_weight / max_possible_weight * 100))
        
        return round(score, 1)
    
    def generate_improvement_suggestions(self, report: QualityReport) -> List[str]:
        """Generate suggestions for improving data quality."""
        suggestions = []
        
        # Group issues by type
        issue_types = {}
        for issue in report.issues:
            if issue.issue_type not in issue_types:
                issue_types[issue.issue_type] = []
            issue_types[issue.issue_type].append(issue)
        
        # Generate suggestions based on issue types
        if 'null_values' in issue_types:
            suggestions.append("Consider adding NOT NULL constraints or default values for critical columns")
        
        if 'invalid_email_format' in issue_types:
            suggestions.append("Implement email validation and normalization during data entry")
        
        if 'inconsistent_phone_format' in issue_types:
            suggestions.append("Standardize phone number format (e.g., +55 11 99999-9999)")
        
        if 'duplicate_values' in issue_types:
            suggestions.append("Add unique constraints to prevent duplicate entries")
        
        if 'inconsistent_case' in issue_types:
            suggestions.append("Implement text normalization (e.g., proper case for names)")
        
        return suggestions


def main():
    """Test the data quality validator."""
    validator = DataQualityValidator("legacy.db")
    report = validator.validate_database()
    
    print(f"Data Quality Report for {report.database_name}")
    print(f"Overall Score: {report.score}/100")
    print(f"Total Issues: {len(report.issues)}")
    
    for issue in report.issues:
        print(f"\n{issue.severity.upper()}: {issue.table}.{issue.column}")
        print(f"  Issue: {issue.description}")
        if issue.sample_values:
            print(f"  Samples: {issue.sample_values}")
    
    suggestions = validator.generate_improvement_suggestions(report)
    print(f"\nImprovement Suggestions:")
    for i, suggestion in enumerate(suggestions, 1):
        print(f"{i}. {suggestion}")


if __name__ == "__main__":
    main()