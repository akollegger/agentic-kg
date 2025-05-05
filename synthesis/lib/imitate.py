#!/usr/bin/env python3
"""
Utility methods for imitating CSV data.
"""
import re
import string
import random
from typing import Dict, List, Any, Optional

import numpy as np
import pandas as pd
from faker import Faker
import nanoid
import inflect

# Import our custom analyzers
from synthesis.lib.title_generator import analyze_and_generate
from synthesis.lib.context_analyzer import analyze_field_contexts

# Initialize Faker and inflect
fake = Faker()
p = inflect.engine()

# Helper function to check if a string is in title case
def is_title_case(text: str) -> bool:
    """Check if a string follows title case convention (most words capitalized)."""
    if not text or not isinstance(text, str):
        return False
        
    # Split the text into words
    words = text.split()
    if not words:
        return False
        
    # Count capitalized words (excluding small words like 'the', 'and', etc. if not at the beginning)
    small_words = {'a', 'an', 'the', 'and', 'but', 'or', 'for', 'nor', 'on', 'at', 'to', 'from', 'by', 'of', 'in'}
    capitalized_count = 0
    
    for i, word in enumerate(words):
        # Skip empty words
        if not word:
            continue
            
        # Check if the word starts with a capital letter
        if word[0].isupper():
            capitalized_count += 1
        # Check if it's a small word not at the beginning
        elif i > 0 and word.lower() in small_words:
            # This is acceptable for title case
            pass
        # If it contains special characters like ':' or '-', check parts separately
        elif any(c in word for c in ':-'):
            # Split by special characters and check each part
            parts = re.split(r'[:;\-]', word)
            if any(part and part[0].isupper() for part in parts if part):
                capitalized_count += 1
    
    # Consider it title case if at least 70% of eligible words are capitalized
    eligible_words = len([w for w in words if w and (w.lower() not in small_words or words.index(w) == 0)])
    return eligible_words > 0 and capitalized_count / eligible_words >= 0.7

# Define field type detection patterns
PATTERNS = {
    'email': r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$',
    'url': r'^(http|https)://',
    'date': r'^\d{4}-\d{2}-\d{2}$',
    'datetime': r'^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}',
    'time': r'^\d{2}:\d{2}(:\d{2})?$',
    'phone': r'^\+?[\d\s\(\)-]{7,20}$',
    'zipcode': r'^\d{5}(-\d{4})?$',
}

def detect_field_types(data: List[Dict[str, Any]], source_path: str = None) -> Dict[str, Dict[str, Any]]:
    """Detect field types with improved multi-value detection and formatting analysis"""
    # Analyze field contexts if source path is provided
    field_contexts = {}
    if source_path and data:
        field_contexts = analyze_field_contexts(source_path, data)
        
    # Define known field relationships
    field_relationships = {
        # Time-based relationships
        'birthYear': {'related_to': 'deathYear', 'relationship': 'before'},
        'birth_year': {'related_to': 'death_year', 'relationship': 'before'},
        'startYear': {'related_to': 'endYear', 'relationship': 'before'},
        'start_year': {'related_to': 'end_year', 'relationship': 'before'},
        'startDate': {'related_to': 'endDate', 'relationship': 'before'},
        'start_date': {'related_to': 'end_date', 'relationship': 'before'},
        
        # Numeric relationships
        'minValue': {'related_to': 'maxValue', 'relationship': 'less_than'},
        'min_value': {'related_to': 'max_value', 'relationship': 'less_than'},
    }
    """
    Detect the type of each field in the CSV data.
    
    Args:
        data: List of dictionaries representing CSV rows
        
    Returns:
        Dictionary mapping field names to their detected types
    """
    if not data:
        return {}
    
    field_types = {}
    multi_value_info = {}
    sample_row = data[0]
    
    for field, value in sample_row.items():
        # Start with string as default type
        field_type = 'string'
        
        # Check if field name is plural, which might indicate a multi-value field
        field_lower = field.lower()
        is_plural = False
        try:
            is_plural = p.plural_noun(field_lower) == field_lower and field_lower != p.singular_noun(field_lower)
        except Exception:
            # Some words might cause issues with inflect
            pass
            
        # Special case for known multi-value fields
        if field_lower in ['genres', 'tags', 'categories', 'keywords', 'actors', 'directors']:
            is_plural = True
        
        # Check for multi-value fields based on content
        if isinstance(value, str):
            for separator in [':', ';', ',', '|', '/']:
                if separator in value and len(value.split(separator)) > 1:
                    # This might be a multi-value field
                    if field not in multi_value_info:
                        multi_value_info[field] = {
                            'separator': separator,
                            'values': set(),
                            'count_samples': [],
                            'is_plural_name': is_plural
                        }
                    
                    # Add the values to our set
                    values = value.split(separator)
                    multi_value_info[field]['count_samples'].append(len(values))
                    for val in values:
                        multi_value_info[field]['values'].add(val.strip())
                    break
        # If field name is plural but no separator was found in this sample, still mark as potential multi-value
        elif is_plural and field not in multi_value_info:
            # Check a few more rows to see if any have separators
            for check_row in data[1:min(5, len(data))]:
                check_value = check_row.get(field, '')
                if isinstance(check_value, str):
                    for separator in [':', ';', ',', '|', '/']:
                        if separator in check_value and len(check_value.split(separator)) > 1:
                            multi_value_info[field] = {
                                'separator': separator,
                                'values': set(),
                                'count_samples': [],
                                'is_plural_name': True
                            }
                            values = check_value.split(separator)
                            multi_value_info[field]['count_samples'].append(len(values))
                            for val in values:
                                multi_value_info[field]['values'].add(val.strip())
                            break
        
        # Skip empty values
        if value is None or value == '':
            # Look at other rows for this field
            for row in data[1:5]:  # Check a few more rows
                if row.get(field) and row.get(field) != '':
                    value = row.get(field)
                    break
            if value is None or value == '':
                field_types[field] = {'type': 'string'}
                continue
                
        # Check if it's a number
        if isinstance(value, (int, float)) or (
            isinstance(value, str) and value and value.replace('.', '', 1).isdigit()
        ):
            try:
                # Check if it's an integer or float
                num_value = float(value)
                if num_value.is_integer():
                    field_type = 'integer'
                    field_types[field] = {
                        'type': field_type,
                        'min': int(num_value),
                        'max': int(num_value),
                        'allow_empty': False
                    }
                else:
                    field_type = 'float'
                    field_types[field] = {
                        'type': field_type,
                        'min': num_value,
                        'max': num_value,
                        'precision': len(str(value).split('.')[-1]) if '.' in str(value) else 2,
                        'allow_empty': False
                    }
                continue
            except (ValueError, TypeError):
                pass
        # Check for empty values in a field that might otherwise be numeric
        elif value == '' or value is None:
            # Mark this field as potentially allowing empty values
            field_types[field] = {
                'type': 'string',  # Default to string for now
                'allow_empty': True,
                'empty_probability': 0.5  # Default probability of empty values
            }
        
        # Check against regex patterns
        for pattern_name, pattern in PATTERNS.items():
            if re.match(pattern, str(value)):
                field_type = pattern_name
                break
                
        # Check for title case formatting
        if field_type == 'string' and isinstance(value, str) and is_title_case(value):
            field_types[field] = {
                'type': 'string',
                'format': 'title_case',
                'context': field_contexts.get(field, None)
            }
            continue
                    
        # Check for boolean values
        if str(value).lower() in ('true', 'false', 'yes', 'no', '1', '0'):
            field_type = 'boolean'
                
        if field_type in ['integer', 'float']:
            # This shouldn't happen as we should have already set field_types above
            # But just in case, set default min/max
            if field_type == 'integer':
                field_types[field] = {'type': field_type, 'min': 0, 'max': 100}
            else:
                field_types[field] = {'type': field_type, 'min': 0.0, 'max': 1.0, 'precision': 2}
        else:
            field_types[field] = {'type': field_type, 'context': field_contexts.get(field, None)}
    
    # Refine detection by checking more rows
    for row in data[1:min(10, len(data))]:
        for field, value in row.items():
            if value is None or value == '':
                continue
                
            current_type = field_types.get(field, {'type': 'string'})
            
            # If current type is numeric but value isn't, downgrade to string
            if current_type['type'] in ('integer', 'float'):
                try:
                    num_value = float(value)
                    
                    # Update min/max values
                    if current_type['type'] == 'integer' and num_value.is_integer():
                        current_min = current_type.get('min', float('inf'))
                        current_max = current_type.get('max', float('-inf'))
                        field_types[field]['min'] = min(current_min, int(num_value))
                        field_types[field]['max'] = max(current_max, int(num_value))
                    elif current_type['type'] == 'float':
                        current_min = current_type.get('min', float('inf'))
                        current_max = current_type.get('max', float('-inf'))
                        field_types[field]['min'] = min(current_min, num_value)
                        field_types[field]['max'] = max(current_max, num_value)
                        
                        # Update precision if needed
                        if '.' in str(value):
                            current_precision = current_type.get('precision', 0)
                            new_precision = len(str(value).split('.')[-1])
                            field_types[field]['precision'] = max(current_precision, new_precision)
                except (ValueError, TypeError):
                    # If we can't convert to float, downgrade to string
                    field_types[field] = {'type': 'string'}
            # Check for empty values
            elif value == '' or value is None:
                # Update empty value probability
                if field_types[field].get('allow_empty', False):
                    # Count empty values to calculate probability
                    empty_count = field_types[field].get('empty_count', 1)
                    field_types[field]['empty_count'] = empty_count + 1
                    # Update probability based on observed data
                    field_types[field]['empty_probability'] = empty_count / (i + 1)
                    
            # Check for multi-value fields in other rows
            if isinstance(value, str) and field in multi_value_info:
                separator = multi_value_info[field]['separator']
                if separator in value:
                    values = value.split(separator)
                    multi_value_info[field]['count_samples'].append(len(values))
                    for val in values:
                        multi_value_info[field]['values'].add(val.strip())
    
    # Check for any fields that should be multi-value but weren't detected
    for field in list(field_types.keys()):
        field_lower = field.lower()
        # Special handling for known multi-value fields like genres
        if field_lower in ['genres', 'tags', 'categories', 'keywords', 'actors', 'directors']:
            # Check if this field has any values with separators
            for row in data[:20]:  # Check first 20 rows
                value = row.get(field, '')
                if not isinstance(value, str):
                    continue
                    
                # Check for common separators
                for separator in [':', ';', ',', '|', '/']:
                    if separator in value and len(value.split(separator)) > 1:
                        # Found a separator, create a multi-value entry
                        if field not in multi_value_info:
                            multi_value_info[field] = {
                                'separator': separator,
                                'values': set(),
                                'count_samples': [],
                                'is_plural_name': True
                            }
                            
                        values = value.split(separator)
                        multi_value_info[field]['count_samples'].append(len(values))
                        for val in values:
                            multi_value_info[field]['values'].add(val.strip())
                        break
    
    # Special handling for deathYear field which often has empty values
    if 'deathYear' in field_types:
        # Mark deathYear as a special case that allows empty values
        non_empty_values = [row.get('deathYear', '') for row in data if row.get('deathYear', '') != '']
        if non_empty_values:
            try:
                # Convert to integers if possible
                valid_years = [int(float(year)) for year in non_empty_values if year and not pd.isna(year)]
                if valid_years:
                    field_types['deathYear'] = {
                        'type': 'integer',
                        'min': min(valid_years),
                        'max': max(valid_years),
                        'allow_empty': True,
                        'empty_probability': len(data) / (len(valid_years) + len(data))
                    }
                else:
                    # If no valid years, treat as string with empty allowed
                    field_types['deathYear'] = {
                        'type': 'string',
                        'allow_empty': True,
                        'empty_probability': 0.7
                    }
            except (ValueError, TypeError):
                # If conversion fails, treat as string with empty allowed
                field_types['deathYear'] = {
                    'type': 'string',
                    'allow_empty': True,
                    'empty_probability': 0.7
                }
    
    # Detect field relationships
    for field in list(field_types.keys()):
        field_lower = field.lower()
        
        # Check for known relationships
        for base_field, relationship in field_relationships.items():
            if field_lower == base_field.lower():
                related_field = relationship['related_to']
                # Look for the related field
                for other_field in field_types:
                    if other_field.lower() == related_field.lower():
                        # Add relationship information to both fields
                        field_types[field]['related_to'] = other_field
                        field_types[field]['relationship'] = relationship['relationship']
                        field_types[other_field]['related_to'] = field
                        field_types[other_field]['relationship'] = 'after' if relationship['relationship'] == 'before' else 'greater_than'
                        break
    
    # Process fields with empty values
    for field, info in field_types.items():
        if info.get('allow_empty', False) and 'empty_count' in info:
            # Calculate final empty probability
            info['empty_probability'] = info['empty_count'] / len(data)
            
            # Determine if this is actually a numeric field that allows empty values
            non_empty_values = [row.get(field, '') for row in data if row.get(field, '') != '']
            if non_empty_values:
                # Check if all non-empty values are numeric
                try:
                    numeric_values = [float(val) for val in non_empty_values]
                    # Filter out NaN values
                    valid_values = [v for v in numeric_values if not np.isnan(v)]
                    
                    if not valid_values:
                        # If all values are NaN, keep as string with empty allowed
                        continue
                        
                    # Check if they're all integers
                    if all(v.is_integer() for v in valid_values):
                        # Update field type to integer with empty allowed
                        field_types[field] = {
                            'type': 'integer',
                            'min': int(min(valid_values)),
                            'max': int(max(valid_values)),
                            'allow_empty': True,
                            'empty_probability': info['empty_probability']
                        }
                    else:
                        # Update field type to float with empty allowed
                        precision = max(len(str(v).split('.')[-1]) if '.' in str(v) else 0 for v in valid_values)
                        field_types[field] = {
                            'type': 'float',
                            'min': min(valid_values),
                            'max': max(valid_values),
                            'precision': precision,
                            'allow_empty': True,
                            'empty_probability': info['empty_probability']
                        }
                except (ValueError, TypeError):
                    # Not all values are numeric, keep as string
                    pass
            
            # Clean up temporary counting fields
            if 'empty_count' in field_types[field]:
                del field_types[field]['empty_count']
    
    # Process multi-value fields and detect enumerated values
    for field, info in multi_value_info.items():
        # Consider it a multi-value field if:
        # 1. We have multiple samples with the separator, or
        # 2. The field name is plural and we found at least one instance with a separator
        if len(info['count_samples']) >= 1 or info.get('is_plural_name', False):
            # Check if this is an enumerated field (values come from a fixed set)
            unique_values = list(info['values'])
            total_occurrences = sum(len(row.get(field, '').split(info['separator'])) 
                                  for row in data if isinstance(row.get(field), str))
            
            # If the number of unique values is small compared to the total occurrences,
            # it's likely an enumerated field
            is_enumerated = len(unique_values) <= 20 and total_occurrences >= 3 * len(unique_values)
            
            field_types[field] = {
                'type': 'multi-value',
                'separator': info['separator'],
                'values': unique_values,
                'avg_count': sum(info['count_samples']) / max(1, len(info['count_samples'])),
                'min_count': min(info['count_samples']) if info['count_samples'] else 1,
                'max_count': max(info['count_samples']) if info['count_samples'] else 1,
                'is_plural_name': info.get('is_plural_name', False),
                'is_enumerated': is_enumerated
            }
    
    return field_types

def get_max_id_value(data: List[Dict[str, Any]], id_field: str) -> Any:
    """
    Get the maximum value of the ID field.
    
    Args:
        data: List of dictionaries representing CSV rows
        id_field: The field to check for maximum value
        
    Returns:
        Maximum value found (or None if field is not numeric)
    """
    try:
        return max(int(row[id_field]) for row in data if row[id_field])
    except (ValueError, TypeError):
        # If not numeric, return None
        return None

def generate_fake_value(field_name: str, field_type_info: Dict[str, Any], row_data: Dict[str, Any] = None, 
                       max_id: Any = None, id_field: bool = False) -> Any:
    """
    Generate a fake value based on field name and type.
    
    Args:
        field_name: Name of the field
        field_type: Detected type of the field
        row_data: Current row data (for reference)
        max_id: Maximum ID value (for ID fields)
        id_field: Whether this is the ID field
        
    Returns:
        Generated fake value
    """
    field_type = field_type_info['type']
    
    # Handle multi-value fields
    if field_type == 'multi-value':
        separator = field_type_info['separator']
        available_values = field_type_info['values']
        
        if not available_values:
            return ""
        
        # Check if this is an enumerated field (like genres)
        is_enumerated = field_type_info.get('is_enumerated', False)
        
        if is_enumerated:
            # For enumerated fields, only use values from the known set
            # Determine how many values to include
            avg_count = field_type_info.get('avg_count', 2)
            min_count = max(1, int(avg_count - 1))
            max_count = int(avg_count + 1)
            count = np.random.randint(min_count, max_count + 1)
            
            # Select random values from the enumerated set
            if len(available_values) <= count:
                # If we don't have enough unique values, use all of them
                selected_values = available_values.copy()
                # Shuffle to avoid always having the same order
                np.random.shuffle(selected_values)
            else:
                # Otherwise, randomly select the required number
                selected_values = np.random.choice(available_values, count, replace=False)
                
            return separator.join(selected_values)
        else:
            # For non-enumerated multi-value fields, we could generate new values
            # but for consistency, we'll still use the available values as a sample
            # Determine how many values to include
            avg_count = field_type_info.get('avg_count', 2)
            min_count = max(1, int(avg_count - 1))
            max_count = int(avg_count + 1)
            count = np.random.randint(min_count, max_count + 1)
            
            # Select random values from the available set
            if len(available_values) <= count:
                # If we don't have enough unique values, use all of them
                selected_values = available_values
            else:
                # Otherwise, randomly select the required number
                selected_values = np.random.choice(available_values, count, replace=False)
                
            return separator.join(selected_values)
    
    # Handle ID field specially
    if id_field:
        if field_type == 'integer' and max_id is not None:
            return max_id + 1 + fake.pyint(min_value=1, max_value=100)
        else:
            return nanoid.generate(size=10)
    
    # Check if this field allows empty values
    if field_type_info.get('allow_empty', False):
        # Determine if we should generate an empty value based on probability
        empty_prob = field_type_info.get('empty_probability', 0.5)
        if random.random() < empty_prob:
            return ''
    
    # Generate based on field type
    if field_type == 'integer':
        min_val = field_type_info.get('min', 0)
        max_val = field_type_info.get('max', 100)
        
        # Ensure min and max are valid
        if min_val >= max_val:
            max_val = min_val + 10
            
        return fake.pyint(min_value=min_val, max_value=max_val)
        
    if field_type == 'float':
        min_val = field_type_info.get('min', 0.0)
        max_val = field_type_info.get('max', 1.0)
        precision = field_type_info.get('precision', 2)
        
        # Ensure min and max are valid
        if min_val >= max_val:
            max_val = min_val + 1.0
            
        # Generate a random float within the range
        value = fake.pyfloat(min_value=min_val, max_value=max_val)
        
        # Round to the appropriate precision
        return round(value, precision)
    elif field_type == 'boolean':
        return fake.boolean()
    elif field_type == 'email':
        return fake.email()
    elif field_type == 'url':
        return fake.url()
    elif field_type == 'date':
        return fake.date()
    elif field_type == 'datetime':
        return fake.date_time().isoformat()
    elif field_type == 'time':
        return fake.time()
    elif field_type == 'phone':
        return fake.phone_number()
    elif field_type == 'zipcode':
        return fake.zipcode()
    
    # Generate based on field name
    field_lower = field_name.lower()
    
    # Check for special formatting
    format_type = field_type_info.get('format', None)
    
    # Check for context-specific field types
    context = field_type_info.get('context', None)
    
    # Handle person name fields
    if context == 'person_name':
        return fake.name()
    
    # Handle company name fields
    if context == 'company_name':
        return fake.company()
    
    # Handle product name fields
    if context == 'product_name':
        return fake.catch_phrase()
    
    # Name-based generation for common fields
    if 'name' in field_lower or field_lower == 'title':
        if format_type == 'title_case':
            # For movie titles, generate a more movie-like title using our analyzer
            if field_lower == 'title':
                # Get source data for analysis
                source_titles = []
                if row_data and 'source_data' in row_data:
                    source_data = row_data.get('source_data', [])
                    # Extract titles from source data
                    source_titles = [row.get('title', '') for row in source_data if row.get('title')][:100]
                
                # If we have source titles, analyze and generate new ones
                if source_titles:
                    return analyze_and_generate(source_titles)[0]
                else:
                    # Fallback to simpler patterns if no source data
                    patterns = [
                        # Single title
                        lambda: string.capwords(fake.catch_phrase()),
                        # Title with subtitle
                        lambda: f"{string.capwords(fake.catch_phrase())}: {string.capwords(fake.bs())}",
                        # Title with 'The'
                        lambda: f"The {string.capwords(fake.catch_phrase())}",
                        # Year-based title
                        lambda: f"{fake.pyint(min_value=1900, max_value=2023)}: {string.capwords(fake.catch_phrase())}"
                    ]
                    return np.random.choice(patterns)()
            # For person name fields with title case
            elif field_lower == 'name' and 'person' in str(row_data.get('source_path', '')).lower():
                return fake.name()
            else:
                # For other title case fields
                return string.capwords(fake.catch_phrase())
        else:
            # Check if this might be a person name based on the file name
            if field_lower == 'name' and 'person' in str(row_data.get('source_path', '')).lower():
                return fake.name()
            return fake.catch_phrase()
    elif 'first' in field_lower and 'name' in field_lower:
        return fake.first_name()
    elif 'last' in field_lower and 'name' in field_lower:
        return fake.last_name()
    elif 'full' in field_lower and 'name' in field_lower:
        return fake.name()
    elif 'user' in field_lower:
        return fake.user_name()
    elif 'company' in field_lower or 'business' in field_lower:
        return fake.company()
    elif 'address' in field_lower:
        if 'street' in field_lower:
            return fake.street_address()
        elif 'city' in field_lower:
            return fake.city()
        elif 'state' in field_lower:
            return fake.state()
        elif 'zip' in field_lower or 'postal' in field_lower:
            return fake.zipcode()
        else:
            return fake.address()
    elif 'phone' in field_lower:
        return fake.phone_number()
    elif 'email' in field_lower:
        return fake.email()
    elif 'birth' in field_lower or 'dob' in field_lower:
        return fake.date_of_birth().strftime('%Y-%m-%d')
    elif 'year' in field_lower:
        return str(fake.year())
    elif 'title' in field_lower:
        return fake.catch_phrase()
    elif 'description' in field_lower or 'summary' in field_lower:
        return fake.paragraph()
    elif 'price' in field_lower or 'cost' in field_lower or 'amount' in field_lower:
        return round(np.random.uniform(10, 1000), 2)
    elif 'quantity' in field_lower or 'count' in field_lower:
        return np.random.randint(1, 100)
    
    # Default to a random string
    return fake.word()

def generate_fake_value_with_constraints(field_name: str, field_type_info: Dict[str, Any], 
                                  row_data: Dict[str, Any], max_id: Any = None, id_field: bool = False) -> Any:
    """
    Generate a fake value that respects constraints with related fields.
    
    Args:
        field_name: Name of the field to generate a value for
        field_type_info: Type information for the field
        row_data: Current row data (for checking related fields)
        max_id: Maximum ID value (for ID fields)
        id_field: Whether this is an ID field
        
    Returns:
        Generated value that respects constraints
    """
    # Check if this field has relationships with other fields
    if 'related_to' in field_type_info and 'relationship' in field_type_info:
        related_field = field_type_info['related_to']
        relationship = field_type_info['relationship']
        
        # If the related field already has a value, apply constraints
        if related_field in row_data and row_data[related_field] != '':
            related_value = row_data[related_field]
            
            # Handle different relationship types
            if relationship == 'before':
                # This field should be before the related field
                if field_type_info['type'] == 'integer':
                    # Ensure this value is less than the related value
                    max_val = int(related_value) - 1
                    min_val = field_type_info.get('min', 0)
                    if min_val >= max_val:
                        # If constraint can't be satisfied, return empty if allowed
                        if field_type_info.get('allow_empty', False):
                            return ''
                        # Otherwise use the min value
                        return min_val
                    # Generate a value between min and max_val
                    return fake.pyint(min_value=min_val, max_value=max_val)
            
            elif relationship == 'after':
                # This field should be after the related field
                if field_type_info['type'] == 'integer':
                    # Ensure this value is greater than the related value
                    min_val = int(related_value) + 1
                    max_val = field_type_info.get('max', 9999)
                    if min_val >= max_val:
                        # If constraint can't be satisfied, return empty if allowed
                        if field_type_info.get('allow_empty', False):
                            return ''
                        # Otherwise use the max value
                        return max_val
                    # Generate a value between min_val and max
                    return fake.pyint(min_value=min_val, max_value=max_val)
    
    # If no constraints or they don't apply, use regular generation
    return generate_fake_value(field_name, field_type_info, row_data, max_id, id_field)


def generate_fake_data(source_data: List[Dict[str, Any]], field_types: Dict[str, Dict[str, Any]], 
                      id_field: str, num_rows: int, source_path: str = None) -> List[Dict[str, Any]]:
    """
    Generate fake data based on the source data structure.
    
    Args:
        source_data: Original CSV data
        field_types: Dictionary of field types
        id_field: Field to treat as ID
        num_rows: Number of rows to generate
        
    Returns:
        List of dictionaries containing fake data
    """
    fake_data = []
    max_id = None
    
    # Get max ID value if ID field is numeric
    if id_field:
        max_id = get_max_id_value(source_data, id_field)
    
    # Generate fake rows
    for i in range(num_rows):
        row = {}
        
        # First pass: generate all non-ID fields
        for field, field_type_info in field_types.items():
            if field == id_field:
                continue
            # Pass source data and path for fields that need it (like title and names)
            row['source_data'] = source_data
            row['source_path'] = source_path
            
            # Use constraint-based generation to ensure logical relationships
            row[field] = generate_fake_value_with_constraints(field, field_type_info, row_data=row)
        
        # Second pass: generate ID field (if specified)
        if id_field:
            row[id_field] = generate_fake_value(id_field, field_types[id_field], 
                                              row_data=row, max_id=max_id, id_field=True)
            # Increment max_id if it's numeric
            if isinstance(max_id, (int, float)):
                max_id = row[id_field]
        
        # Remove the source_data and source_path before adding to results
        if 'source_data' in row:
            del row['source_data']
        if 'source_path' in row:
            del row['source_path']
            
        # Add to results
        fake_data.append(row)
    
    return fake_data