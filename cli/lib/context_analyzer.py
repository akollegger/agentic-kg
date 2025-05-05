#!/usr/bin/env python3
"""
Context Analyzer - Analyze field context to determine appropriate data types and generation methods.
"""
import os
import re
from typing import Dict, List, Any, Set, Tuple, Optional

class ContextAnalyzer:
    """
    Analyzes the context of fields to determine their semantic meaning.
    """
    
    # Field name patterns that strongly indicate person names
    PERSON_NAME_PATTERNS = [
        r'^name$',
        r'^full[_\s]*name$',
        r'^person[_\s]*name$',
        r'^author[_\s]*name$',
        r'^director[_\s]*name$',
        r'^actor[_\s]*name$',
        r'^(first|last)[_\s]*name$',
    ]
    
    # Field name patterns that indicate company or organization names
    COMPANY_NAME_PATTERNS = [
        r'^company[_\s]*name$',
        r'^organization[_\s]*name$',
        r'^business[_\s]*name$',
        r'^employer[_\s]*name$',
        r'^publisher[_\s]*name$',
        r'^studio[_\s]*name$',
    ]
    
    # Field name patterns that indicate product or item names
    PRODUCT_NAME_PATTERNS = [
        r'^product[_\s]*name$',
        r'^item[_\s]*name$',
        r'^model[_\s]*name$',
        r'^brand[_\s]*name$',
    ]
    
    # File name patterns that indicate person-related data
    PERSON_FILE_PATTERNS = [
        r'people',
        r'persons',
        r'users',
        r'customers',
        r'employees',
        r'authors',
        r'directors',
        r'actors',
        r'cast',
        r'crew',
    ]
    
    # Person-related fields that often appear together
    PERSON_RELATED_FIELDS = {
        'birthdate', 'birth_date', 'birthYear', 'birth_year', 'dob',
        'deathdate', 'death_date', 'deathYear', 'death_year', 'dod',
        'age', 'gender', 'nationality', 'occupation', 'profession',
        'email', 'phone', 'address', 'city', 'country',
    }
    
    def __init__(self):
        self.file_context = None
        self.field_contexts = {}
    
    def analyze_file_context(self, file_path: str) -> str:
        """Analyze the file name to determine context."""
        file_name = os.path.basename(file_path).lower()
        file_name_no_ext = os.path.splitext(file_name)[0]
        
        # Check for person-related file names
        for pattern in self.PERSON_FILE_PATTERNS:
            if re.search(pattern, file_name_no_ext, re.IGNORECASE):
                return 'person'
        
        # Check for other common contexts
        if re.search(r'compan(y|ies)', file_name_no_ext, re.IGNORECASE):
            return 'company'
        if re.search(r'product', file_name_no_ext, re.IGNORECASE):
            return 'product'
        if re.search(r'movie|film', file_name_no_ext, re.IGNORECASE):
            return 'movie'
        if re.search(r'book', file_name_no_ext, re.IGNORECASE):
            return 'book'
        
        return 'unknown'
    
    def analyze_field_name_context(self, field_name: str) -> str:
        """Analyze the field name to determine context."""
        field_lower = field_name.lower()
        
        # Check for person name patterns
        for pattern in self.PERSON_NAME_PATTERNS:
            if re.search(pattern, field_lower, re.IGNORECASE):
                return 'person_name'
        
        # Check for company name patterns
        for pattern in self.COMPANY_NAME_PATTERNS:
            if re.search(pattern, field_lower, re.IGNORECASE):
                return 'company_name'
        
        # Check for product name patterns
        for pattern in self.PRODUCT_NAME_PATTERNS:
            if re.search(pattern, field_lower, re.IGNORECASE):
                return 'product_name'
        
        # Check for other common fields
        if field_lower == 'title':
            return 'title'
        
        return 'unknown'
    
    def analyze_related_fields(self, fields: List[str]) -> Dict[str, str]:
        """Analyze relationships between fields to determine context."""
        fields_lower = [f.lower() for f in fields]
        
        # Count person-related fields
        person_field_count = sum(1 for f in fields_lower if f in self.PERSON_RELATED_FIELDS)
        
        # If we have multiple person-related fields, this is likely a person dataset
        if person_field_count >= 2:
            # Look for generic name fields that might be person names
            contexts = {}
            for field in fields:
                if field.lower() == 'name':
                    contexts[field] = 'person_name'
            return contexts
        
        return {}
    
    def analyze_name_values(self, values: List[str]) -> str:
        """Analyze name values to determine if they look like person names."""
        # Count values that match person name patterns
        person_name_count = 0
        
        for value in values:
            if not isinstance(value, str) or not value:
                continue
            
            # Check for common person name patterns
            # 1. First Last format
            if re.match(r'^[A-Z][a-z]+ [A-Z][a-z]+$', value):
                person_name_count += 1
            # 2. First Middle Last format
            elif re.match(r'^[A-Z][a-z]+ [A-Z][a-z]+ [A-Z][a-z]+$', value):
                person_name_count += 1
            # 3. Last, First format
            elif re.match(r'^[A-Z][a-z]+, [A-Z][a-z]+$', value):
                person_name_count += 1
        
        # If more than 70% of values look like person names, it's likely a person name field
        if person_name_count / max(1, len(values)) > 0.7:
            return 'person_name'
        
        return 'unknown'
    
    def analyze_context(self, file_path: str, data: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        Analyze the context of a dataset to determine field semantics.
        
        Args:
            file_path: Path to the source file
            data: List of dictionaries representing the data
            
        Returns:
            Dictionary mapping field names to their semantic contexts
        """
        if not data:
            return {}
        
        # Analyze file context
        self.file_context = self.analyze_file_context(file_path)
        
        # Get all field names
        fields = list(data[0].keys())
        
        # Initialize contexts
        contexts = {}
        
        # Analyze each field name
        for field in fields:
            context = self.analyze_field_name_context(field)
            if context != 'unknown':
                contexts[field] = context
        
        # Analyze related fields
        related_contexts = self.analyze_related_fields(fields)
        contexts.update(related_contexts)
        
        # For fields with unknown context, analyze values
        for field in fields:
            if field not in contexts and field.lower() == 'name':
                # Get sample values (up to 20)
                values = [row.get(field, '') for row in data[:20] if row.get(field)]
                
                # Analyze values
                value_context = self.analyze_name_values(values)
                if value_context != 'unknown':
                    contexts[field] = value_context
                # If file context is person-related, assume name is person name
                elif self.file_context == 'person':
                    contexts[field] = 'person_name'
        
        return contexts


def analyze_field_contexts(file_path: str, data: List[Dict[str, Any]]) -> Dict[str, str]:
    """
    Analyze the context of fields in a dataset.
    
    Args:
        file_path: Path to the source file
        data: List of dictionaries representing the data
        
    Returns:
        Dictionary mapping field names to their semantic contexts
    """
    analyzer = ContextAnalyzer()
    return analyzer.analyze_context(file_path, data)
