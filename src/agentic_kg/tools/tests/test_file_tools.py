"""
Tests for the file_tools module."""

import os
import tempfile
from pathlib import Path
from unittest import TestCase, mock

from agentic_kg.tools.file_tools import (
    list_import_files, sample_markdown_file, get_neo4j_import_directory,
    sample_csv_file, show_sample, search_file
)


class TestFileTools(TestCase):
    """Test cases for the file_tools module."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for test files
        self.temp_dir = tempfile.TemporaryDirectory()
        self.import_dir = Path(self.temp_dir.name) / "import"
        self.import_dir.mkdir()
        
        # Create test files with different extensions
        (self.import_dir / "data.csv").write_text("id,name\n1,test\n")
        (self.import_dir / "notes.md").write_text("# Test\n\nMarkdown content")
        (self.import_dir / "config.txt").write_text("key=value")
        (self.import_dir / "unsupported.log").write_text("log entry")
        (self.import_dir / "md_empty.md").write_text("")

        # Create a subdirectory with more files
        subdir = self.import_dir / "subdir"
        subdir.mkdir()
        (subdir / "more_data.csv").write_text("id,value\n1,test\n")

        # Create markdown file specifically for search testing
        # Note: search_file does not parse frontmatter, so it's treated as plain text.
        (self.import_dir / "search_test.md").write_text(
            "---\n"
            "title: Searchable Document\n"
            "keywords: test, search, markdown\n"
            "---\n"
            "# Search Test Document\n"
            "\n"
            "This is line 1 with searchable content.\n"
            "This is line 2 with different content.\n"
            "This is line 3 with SEARCHABLE content (case different).\n"
            "This is line 4 without the term.\n"
            "This is line 5 with the term searchable again.\n"
        )

        # Create CSV files for testing search_csv_file and sample_csv_file
        (self.import_dir / "search_data.csv").write_text(
            "ID,Name,Category,Description\n"
            "1,Apple,Fruit,A round red fruit\n"
            "2,Banana,Fruit,A long yellow fruit\n"
            "3,Carrot,Vegetable,An orange root vegetable\n"
            "4,apple pie,Dessert,A pie made with apples\n"
            "5,Orange Juice,Beverage,Juice from oranges\n"
        )
        (self.import_dir / "empty_search.csv").write_text("")
        (self.import_dir / "header_only_search.csv").write_text("ColA,ColB,ColC\n")
        
        # Mock the tool context
        self.tool_context = mock.MagicMock()
        self.tool_context.state = {}
        
        # Patch get_import_directory to return our test directory
        self.get_import_dir_patcher = mock.patch(
            'agentic_kg.tools.file_tools.graphdb.get_import_directory',
            return_value={
                'status': 'success',
                'neo4j_import_dir': str(self.import_dir)
            }
        )
        self.mock_get_import_dir = self.get_import_dir_patcher.start()
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.get_import_dir_patcher.stop()
        self.temp_dir.cleanup()
    
    def test_list_import_files_returns_supported_files(self):
        """Test that list_import_files returns only supported file types."""
        result = list_import_files(self.tool_context)
        
        self.assertEqual(result['status'], 'success')
        self.assertIn('files', result)
        
        # Convert to set for easier comparison
        files = set(Path(f).name for f in result['files'])
        
        # Should include supported files
        self.assertIn('data.csv', files)
        self.assertIn('notes.md', files)
        self.assertIn('config.txt', files)
        self.assertIn('subdir/more_data.csv', result['files'])
        
        # Should not include unsupported files
        self.assertNotIn('unsupported.log', files)
    
    def test_list_import_files_includes_files_in_subdirectories(self):
        """Test that list_import_files includes files in subdirectories."""
        result = list_import_files(self.tool_context)
        
        self.assertEqual(result['status'], 'success')
        self.assertIn('subdir/more_data.csv', result['files'])
    
    def test_list_import_files_handles_missing_directory(self):
        """Test that list_import_files handles missing import directory."""
        # Mock get_import_directory to return an error
        self.mock_get_import_dir.return_value = {
            'status': 'error',
            'error_message': 'Directory not found'
        }
        
        result = list_import_files(self.tool_context)
        
        self.assertEqual(result['status'], 'error')
        self.assertIn('error_message', result)
        self.assertEqual(result['error_message'], 'Directory not found')

    def test_sample_markdown_file(self):
        """Test sampling a markdown file."""
        result = sample_markdown_file("notes.md", self.tool_context)
        self.assertEqual(result['status'], 'success')
        self.assertIn('samples', result)
        sample = result['samples']
        self.assertEqual(sample['metadata']['path'], "notes.md")
        self.assertEqual(sample['metadata']['mimetype'], "text/markdown")
        self.assertNotIn('frontmatter', sample) # Ensure frontmatter key is removed
        expected_content = "# Test\n\nMarkdown content"
        self.assertEqual(sample['content'], expected_content)

    def test_sample_markdown_empty_file(self):
        """Test sampling an empty markdown file."""
        result = sample_markdown_file("md_empty.md", self.tool_context)
        self.assertEqual(result['status'], 'success')
        sample = result['samples']
        self.assertNotIn('frontmatter', sample) # Ensure frontmatter key is removed
        self.assertEqual(sample['content'], "")

    def test_sample_markdown_file_not_exists(self):
        """Test sampling a non-existent markdown file."""
        result = sample_markdown_file("non_existent.md", self.tool_context)
        self.assertEqual(result['status'], 'error')
        self.assertIn("Path does not exist: non_existent.md", result.get('error_message', ''))

    # Tests for search_csv_file removed - using only search_file
    # --- Tests for show_sample (after fix) --- 
    def test_show_sample_csv_exists(self):
        """Test showing a previously sampled CSV file."""
        # First, sample the file
        sample_csv_file("data.csv", 1, self.tool_context) # Sample 1 row
        
        result = show_sample("data.csv", self.tool_context)
        self.assertEqual(result['status'], 'success')
        retrieved_sample = result['retrieved_sample']
        self.assertEqual(retrieved_sample['metadata']['path'], "data.csv")
        self.assertEqual(retrieved_sample['metadata']['mimetype'], "text/csv")
        self.assertEqual(len(retrieved_sample['data']), 1) # We sampled 1 row
        # The first row is the header row
        self.assertEqual(retrieved_sample['data'][0], ['id', 'name'])

    def test_show_sample(self):
        """Test showing a previously sampled file."""
        # First, sample a file (using notes.md as it's simpler)
        sample_markdown_file("notes.md", self.tool_context)
        
        result = show_sample("notes.md", self.tool_context)
        self.assertEqual(result['status'], 'success')
        retrieved_sample = result['retrieved_sample']
        self.assertEqual(retrieved_sample['metadata']['path'], "notes.md")
        # Check some expected keys, actual content checked in sample_markdown_file test
        self.assertNotIn('frontmatter', retrieved_sample) # Ensure frontmatter key is removed
        self.assertIn('content', retrieved_sample)
        self.assertIn('annotations', retrieved_sample)

    def test_show_sample_path_not_sampled(self):
        """Test showing a sample for a path that has not been sampled."""
        # Initialize the samples dictionary to test the specific case where samples exist but not for this path
        self.tool_context.state["samples"] = {"some_other_path": {"data": "dummy_data"}}
        result = show_sample("search_data.csv", self.tool_context) # This file exists but hasn't been 'sampled'
        self.assertEqual(result['status'], 'error')
        self.assertIn("No sample found for path: search_data.csv", result.get('error_message', ''))

    def test_show_sample_no_samples_in_context(self):
        """Test showing a sample when tool_context.state['samples'] is not initialized."""
        self.tool_context.state = {} # Reset state to ensure 'samples' key is missing
        result = show_sample("data.csv", self.tool_context)
        self.assertEqual(result['status'], 'error')
        self.assertIn("No samples have been taken yet.", result.get('error_message', ''))

    def test_show_sample_file_does_not_exist_in_filesystem(self):
        """Test showing a sample for a path that does not exist in the filesystem (but could have been sampled)."""
        # Simulate a sample was taken for a file that was later deleted
        sample_path_abs = str(self.import_dir / "deleted_file.csv")
        self.tool_context.state["samples"] = {
            sample_path_abs: {"metadata": {"path": "deleted_file.csv"}, "data": ["some_data"]}
        }
        result = show_sample("deleted_file.csv", self.tool_context)
        self.assertEqual(result['status'], 'success') # show_sample retrieves from state, doesn't re-check filesystem
        self.assertEqual(result['retrieved_sample']['metadata']['path'], "deleted_file.csv")
        
    # Tests for search_markdown_file removed - using only search_file
    # --- Tests for search_file (unified search) --- 
    def test_search_file_csv(self):
        """Test searching a CSV file using the unified search_file function."""
        result = search_file("search_data.csv", "apple", self.tool_context)
        self.assertEqual(result['status'], 'success')
        search_results = result['search_results']
        self.assertTrue(search_results['metadata']['lines_found'] > 0)
        # Verify we have matching lines
        self.assertTrue(len(search_results['matching_lines']) > 0)
        
    def test_search_file_markdown(self):
        """Test searching a Markdown file using the unified search_file function."""
        result = search_file("search_test.md", "searchable", self.tool_context)
        self.assertEqual(result['status'], 'success')
        search_results = result['search_results']
        self.assertTrue(search_results['metadata']['lines_found'] > 0)
        
    def test_search_file_plain_text(self):
        """Test searching a plain text file using the unified search_file function."""
        # Create a plain text file
        (self.import_dir / "plain.txt").write_text("This is line 1\nThis is line 2 with searchterm\nThis is line 3")
        
        result = search_file("plain.txt", "searchterm", self.tool_context)
        self.assertEqual(result['status'], 'success')
        search_results = result['search_results']
        self.assertEqual(search_results['metadata']['lines_found'], 1)
        self.assertEqual(search_results['matching_lines'][0]['line_number'], 2)
        
    def test_search_file_case_insensitivity(self):
        """Test case insensitivity in the unified search_file function."""
        # Create a plain text file with mixed case
        (self.import_dir / "case_test.txt").write_text("This is UPPERCASE\nThis is lowercase")
        
        # Search should be case insensitive
        result = search_file("case_test.txt", "uppercase", self.tool_context)
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['search_results']['metadata']['lines_found'], 1)
        
        # Should also find with different case
        result = search_file("case_test.txt", "UPPERCASE", self.tool_context)
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['search_results']['metadata']['lines_found'], 1)
        
    def test_search_file_empty_query(self):
        """Test searching with an empty query using the unified search_file function."""
        result = search_file("search_data.csv", "", self.tool_context)
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['search_results']['metadata']['lines_found'], 0)
        
    def test_search_file_nonexistent(self):
        """Test searching a non-existent file using the unified search_file function."""
        result = search_file("nonexistent.txt", "query", self.tool_context)
        self.assertEqual(result['status'], 'error')
        self.assertIn("File does not exist", result.get('error_message', ''))
