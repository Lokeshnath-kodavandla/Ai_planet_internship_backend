import sqlite3
from pathlib import Path

# Database file path
DB_PATH = Path("pdf_qa.db")

def get_db():
    """
    Database dependency for FastAPI
    Returns a database connection that will be automatically closed
    """
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    """
    Initialize the database with required tables
    """
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    # Create pdf_documents table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pdf_documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            file_path TEXT NOT NULL,
            upload_date TEXT NOT NULL,
            file_size INTEGER NOT NULL,
            extracted_text TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create an index on filename for faster searches
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_filename ON pdf_documents(filename)
    """)
    
    conn.commit()
    conn.close()
    
    print("Database initialized successfully")

if __name__ == "__main__":
    # Initialize database when run directly
    init_db()
