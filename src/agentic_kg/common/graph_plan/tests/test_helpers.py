"""
Tests for the planning module.
"""

import os
import csv
import tempfile
import unittest
from pathlib import Path

from agentic_kg.common.graph_plan.helpers import (
    file_source_from_file,
    create_initial_graph_plan
)
from agentic_kg.common.graph_plan import FileSource


class TestHelpers(unittest.TestCase):
    """Test cases for the helpers module."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for test files
        self.temp_dir = tempfile.TemporaryDirectory()
        
        # Create a test CSV file
        self.csv_path = os.path.join(self.temp_dir.name, "people.csv")
        with open(self.csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["id", "name", "age", "email"])
            writer.writerow(["1", "Alice", "30", "alice@example.com"])
            writer.writerow(["2", "Bob", "25", "bob@example.com"])
        
        # Create a test text file
        self.txt_path = os.path.join(self.temp_dir.name, "notes.txt")
        with open(self.txt_path, 'w') as f:
            f.write("These are some notes about the project.")
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.temp_dir.cleanup()
    
    def test_file_source_from_file_csv(self):
        """Test creating a FileSource from a CSV file."""
        source = file_source_from_file(self.csv_path)
        
        self.assertIsInstance(source, FileSource)
        self.assertEqual(source.file_path, self.csv_path)
        self.assertEqual(source.mime_type, "text/csv")
        self.assertEqual(source.header, ["id", "name", "age", "email"])
    
    def test_file_source_from_file_txt(self):
        """Test creating a FileSource from a text file."""
        source = file_source_from_file(self.txt_path)
        
        self.assertIsInstance(source, FileSource)
        self.assertEqual(source.file_path, self.txt_path)
        self.assertEqual(source.mime_type, "text/plain")
        self.assertEqual(source.header, [])
    
    def test_file_source_from_file_not_found(self):
        """Test creating a FileSource from a non-existent file."""
        with self.assertRaises(FileNotFoundError):
            file_source_from_file("/path/to/nonexistent/file.csv")
    
    def test_create_initial_graph_plan(self):
        """Test creating an initial graph plan."""
        graph_plan = create_initial_graph_plan(
            name="Test Graph Plan",
            description="A test graph plan",
            file_paths=[self.csv_path, self.txt_path]
        )
        
        # Check the graph plan properties
        self.assertEqual(graph_plan.name, "Test Graph Plan")
        self.assertEqual(graph_plan.description, "A test graph plan")
        
        # Should have two file sources
        self.assertEqual(len(graph_plan.sources), 2)
        
        # Check that the file sources are correct
        self.assertIn(self.csv_path, graph_plan.sources)
        self.assertIn(self.txt_path, graph_plan.sources)
        
        # Check the CSV file source
        csv_source = graph_plan.sources[self.csv_path]
        self.assertEqual(csv_source.mime_type, "text/csv")
        self.assertEqual(csv_source.header, ["id", "name", "age", "email"])
        
        # Check the text file source
        txt_source = graph_plan.sources[self.txt_path]
        self.assertEqual(txt_source.mime_type, "text/plain")
        self.assertEqual(txt_source.header, [])


if __name__ == "__main__":
    unittest.main()
