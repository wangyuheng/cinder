"""
Unit tests for context management.
"""

from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import unittest

from cinder_cli.agents.context import InMemoryContextManager
from cinder_cli.agents.context_manager import ContextManager


class TestInMemoryContextManager(unittest.TestCase):
    """Test cases for InMemoryContextManager."""
    
    def setUp(self):
        self.manager = InMemoryContextManager(max_size_mb=1)
    
    def test_set_and_get(self):
        self.manager.set("key1", "value1")
        self.assertEqual(self.manager.get("key1"), "value1")
    
    def test_get_nonexistent_key(self):
        self.assertIsNone(self.manager.get("nonexistent"))
        self.assertEqual(self.manager.get("nonexistent", "default"), "default")
    
    def test_delete(self):
        self.manager.set("key1", "value1")
        self.assertTrue(self.manager.delete("key1"))
        self.assertIsNone(self.manager.get("key1"))
        self.assertFalse(self.manager.delete("nonexistent"))
    
    def test_query_by_scope(self):
        self.manager.set("key1", "value1", scope="session")
        self.manager.set("key2", "value2", scope="user")
        
        results = self.manager.query({"scope": "session"})
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].key, "key1")
    
    def test_query_by_time_range(self):
        now = datetime.now()
        past = now - timedelta(hours=1)
        future = now + timedelta(hours=1)
        
        self.manager.set("key1", "value1")
        
        results = self.manager.query({"after": past})
        self.assertEqual(len(results), 1)
        
        results = self.manager.query({"after": future})
        self.assertEqual(len(results), 0)
    
    def test_clear_all(self):
        self.manager.set("key1", "value1")
        self.manager.set("key2", "value2")
        
        self.manager.clear()
        self.assertEqual(self.manager.get_entry_count(), 0)
    
    def test_clear_by_scope(self):
        self.manager.set("key1", "value1", scope="session")
        self.manager.set("key2", "value2", scope="user")
        
        self.manager.clear(scope="session")
        self.assertIsNone(self.manager.get("key1"))
        self.assertEqual(self.manager.get("key2"), "value2")


class TestContextManager(unittest.TestCase):
    """Test cases for ContextManager."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_context.db"
        self.manager = ContextManager(
            db_path=self.db_path,
            user_id="test_user",
            project_id="test_project",
            session_id="test_session",
        )
    
    def tearDown(self):
        if self.db_path.exists():
            self.db_path.unlink()
    
    def test_set_and_get_short_term(self):
        self.manager.set("key1", "value1")
        self.assertEqual(self.manager.get("key1"), "value1")
    
    def test_persist_and_load(self):
        self.manager.set("key1", "value1", scope="user")
        self.manager.save()
        
        new_manager = ContextManager(
            db_path=self.db_path,
            user_id="test_user",
            project_id="test_project",
        )
        new_manager.load()
        
        self.assertEqual(new_manager.get("key1"), "value1")
    
    def test_context_isolation_by_user(self):
        self.manager.set("key1", "value1")
        
        other_manager = ContextManager(
            db_path=self.db_path,
            user_id="other_user",
            project_id="test_project",
        )
        
        self.assertIsNone(other_manager.get("key1"))
    
    def test_context_isolation_by_project(self):
        self.manager.set("key1", "value1")
        
        other_manager = ContextManager(
            db_path=self.db_path,
            user_id="test_user",
            project_id="other_project",
        )
        
        self.assertIsNone(other_manager.get("key1"))
    
    def test_query_from_database(self):
        self.manager.set("key1", "value1", scope="user")
        self.manager.set("key2", "value2", scope="session")
        self.manager.save()
        
        results = self.manager.query({"scope": "user"})
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].key, "key1")
    
    def test_cleanup_old_entries(self):
        old_time = datetime.now() - timedelta(days=31)
        self.manager.set("old_key", "old_value", scope="session")
        self.manager.entries["old_key"].timestamp = old_time
        self.manager.save()
        
        self.manager.set("new_key", "new_value", scope="session")
        self.manager.save()
        
        removed = self.manager.cleanup_old_entries()
        self.assertGreater(removed, 0)
    
    def test_get_statistics(self):
        self.manager.set("key1", "value1", scope="session")
        self.manager.set("key2", "value2", scope="user")
        self.manager.save()
        
        stats = self.manager.get_statistics()
        
        self.assertEqual(stats["total_entries"], 2)
        self.assertEqual(stats["session_entries"], 1)
        self.assertEqual(stats["user_entries"], 1)
        self.assertGreater(stats["short_term_entries"], 0)


if __name__ == "__main__":
    unittest.main()
