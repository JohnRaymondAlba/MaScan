# src/database/__init__.py
"""Database package with lazy initialization."""

from .db_manager import Database

# Singleton instance (lazy-loaded)
_db_instance = None

class LazyDatabase:
    """Lazy-loading database wrapper for serverless environments."""
    
    def __getattr__(self, name):
        """Lazy initialize database on first attribute access."""
        global _db_instance
        if _db_instance is None:
            _db_instance = Database()
        return getattr(_db_instance, name)

# Use this as the default db object in routes
db = LazyDatabase()

def get_db():
    """Get or create database instance explicitly."""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance