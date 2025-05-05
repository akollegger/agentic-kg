#!/usr/bin/env python3
"""
Title Generator - Advanced title generation using pattern analysis.
"""
import re
import random
import string
from collections import Counter, defaultdict
from typing import List, Dict, Any, Tuple, Set, Optional

class TitleAnalyzer:
    """
    Analyzes existing titles to extract patterns and vocabulary for generating new titles.
    Uses a simplified NLP approach that doesn't require external models.
    """
    
    # Common words that are typically lowercase in titles unless at the beginning
    SMALL_WORDS = {'a', 'an', 'the', 'and', 'but', 'or', 'for', 'nor', 'on', 'at', 
                  'to', 'from', 'by', 'of', 'in', 'with', 'as'}
    
    # Common patterns in movie titles
    TITLE_PATTERNS = [
        # Simple title
        "{adj} {noun}",
        "The {adj} {noun}",
        "{noun} {noun}",
        # Title with subtitle
        "{noun}: {adj} {noun}",
        "{adj} {noun}: {noun}",
        # Title with "of the"
        "{noun} of the {noun}",
        "{noun} of {adj} {noun}",
        # Year-based title
        "{year}: {adj} {noun}",
        # Action titles
        "The Last {noun}",
        "{verb}ing the {noun}"
    ]
    
    def __init__(self):
        # Vocabulary extracted from titles
        self.nouns: Set[str] = set()
        self.verbs: Set[str] = set()
        self.adjectives: Set[str] = set()
        self.patterns: List[str] = []
        self.pattern_counts: Counter = Counter()
        self.title_parts: Dict[str, Set[str]] = defaultdict(set)
        self.common_prefixes: List[str] = []
        self.common_suffixes: List[str] = []
        self.min_year: int = 1900
        self.max_year: int = 2025
        
    def is_likely_noun(self, word: str) -> bool:
        """Heuristic to identify likely nouns."""
        # Most nouns are capitalized in titles
        if not word[0].isupper():
            return False
            
        # Common noun endings
        noun_endings = ('er', 'or', 'ist', 'ism', 'ion', 'ity', 'ment', 'ness', 'ship')
        return (
            word.lower() not in self.SMALL_WORDS and
            (word.endswith(noun_endings) or True)  # Default to True for simplicity
        )
    
    def is_likely_adjective(self, word: str) -> bool:
        """Heuristic to identify likely adjectives."""
        # Common adjective endings
        adj_endings = ('al', 'ful', 'ic', 'ive', 'less', 'ous', 'able', 'ible')
        return (
            word[0].isupper() and 
            word.lower() not in self.SMALL_WORDS and
            any(word.lower().endswith(ending) for ending in adj_endings)
        )
    
    def is_likely_verb(self, word: str) -> bool:
        """Heuristic to identify likely verbs."""
        # Common verb endings
        verb_endings = ('ing', 'ed', 'ize', 'ise', 'ate', 'ify')
        return any(word.lower().endswith(ending) for ending in verb_endings)
    
    def extract_pattern(self, title: str) -> str:
        """Extract a simplified pattern from a title."""
        words = title.split()
        pattern = []
        
        for i, word in enumerate(words):
            word_clean = re.sub(r'[^\w\s]', '', word).strip()
            if not word_clean:
                pattern.append("{punct}")
                continue
                
            if i == 0 or word not in self.SMALL_WORDS:
                if self.is_likely_adjective(word_clean):
                    pattern.append("{adj}")
                    self.adjectives.add(word_clean)
                elif self.is_likely_verb(word_clean):
                    pattern.append("{verb}")
                    self.verbs.add(word_clean)
                elif self.is_likely_noun(word_clean):
                    pattern.append("{noun}")
                    self.nouns.add(word_clean)
                elif word_clean.isdigit() and len(word_clean) == 4:
                    pattern.append("{year}")
                    year = int(word_clean)
                    if 1900 <= year <= 2025:
                        self.min_year = min(self.min_year, year)
                        self.max_year = max(self.max_year, year)
                else:
                    pattern.append(word_clean)
            else:
                pattern.append(word_clean.lower())
        
        return " ".join(pattern)
    
    def analyze_titles(self, titles: List[str]) -> None:
        """Analyze a list of titles to extract patterns and vocabulary."""
        for title in titles:
            # Skip empty titles
            if not title or not isinstance(title, str):
                continue
                
            # Extract pattern
            pattern = self.extract_pattern(title)
            self.patterns.append(pattern)
            self.pattern_counts[pattern] += 1
            
            # Extract common prefixes
            parts = title.split(':')
            if len(parts) > 1:
                self.title_parts['prefix'].add(parts[0].strip())
                self.title_parts['suffix'].add(parts[1].strip())
                
            # Extract words by position
            words = title.split()
            if words:
                self.title_parts['first_word'].add(words[0])
                self.title_parts['last_word'].add(words[-1])
        
        # Get most common patterns
        self.common_patterns = [p for p, _ in self.pattern_counts.most_common(10)]
        
        # Get common prefixes and suffixes
        self.common_prefixes = list(self.title_parts['prefix'])
        self.common_suffixes = list(self.title_parts['suffix'])
        
        # If we didn't find enough vocabulary, add some defaults
        if len(self.nouns) < 10:
            self.nouns.update([
                "Adventure", "Journey", "Quest", "Hero", "Legend", "Secret", 
                "Mission", "Destiny", "Story", "Dream", "Night", "Day", "World"
            ])
            
        if len(self.adjectives) < 10:
            self.adjectives.update([
                "Dark", "Final", "Eternal", "Lost", "Hidden", "Forbidden", 
                "Ultimate", "Great", "Last", "First", "New", "Old"
            ])
            
        if len(self.verbs) < 5:
            self.verbs.update([
                "Finding", "Saving", "Discovering", "Fighting", "Escaping",
                "Conquering", "Revealing", "Transforming", "Breaking", "Making"
            ])


class TitleGenerator:
    """
    Generates new titles based on analyzed patterns and vocabulary.
    """
    
    def __init__(self, analyzer: TitleAnalyzer):
        self.analyzer = analyzer
        
    def apply_title_case(self, text: str) -> str:
        """Apply proper title case formatting."""
        words = text.split()
        result = []
        
        for i, word in enumerate(words):
            # Always capitalize first and last word
            if i == 0 or i == len(words) - 1:
                result.append(word.capitalize())
            # Don't capitalize small words unless they're the first word
            elif word.lower() in self.analyzer.SMALL_WORDS:
                result.append(word.lower())
            # Capitalize other words
            else:
                result.append(word.capitalize())
                
        return " ".join(result)
    
    def generate_from_pattern(self, pattern: str) -> str:
        """Generate a title from a pattern."""
        # Replace placeholders with random words from our vocabulary
        result = pattern
        
        # Replace {noun} placeholders
        while "{noun}" in result and self.analyzer.nouns:
            result = result.replace("{noun}", random.choice(list(self.analyzer.nouns)), 1)
            
        # Replace {adj} placeholders
        while "{adj}" in result and self.analyzer.adjectives:
            result = result.replace("{adj}", random.choice(list(self.analyzer.adjectives)), 1)
            
        # Replace {verb} placeholders
        while "{verb}" in result and self.analyzer.verbs:
            result = result.replace("{verb}", random.choice(list(self.analyzer.verbs)), 1)
            
        # Replace {year} placeholders
        while "{year}" in result:
            year = random.randint(self.analyzer.min_year, self.analyzer.max_year)
            result = result.replace("{year}", str(year), 1)
            
        # Apply title case
        return self.apply_title_case(result)
    
    def generate_title(self) -> str:
        """Generate a new title based on analyzed patterns."""
        # Choose a pattern: 70% from common patterns, 30% from predefined patterns
        if self.analyzer.patterns and random.random() < 0.7:
            # Use a pattern we extracted from real titles
            pattern = random.choice(self.analyzer.patterns)
        else:
            # Use a predefined pattern
            pattern = random.choice(self.analyzer.TITLE_PATTERNS)
            
        return self.generate_from_pattern(pattern)
    
    def generate_titles(self, count: int = 1) -> List[str]:
        """Generate multiple titles."""
        return [self.generate_title() for _ in range(count)]


# Example usage
def analyze_and_generate(source_titles: List[str], count: int = 1) -> List[str]:
    """Analyze source titles and generate new ones."""
    analyzer = TitleAnalyzer()
    analyzer.analyze_titles(source_titles)
    
    generator = TitleGenerator(analyzer)
    return generator.generate_titles(count)
