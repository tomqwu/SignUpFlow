"""Migration: Make assignments.solution_id nullable."""

import sqlite3

def migrate():
    """Make solution_id nullable in assignments table."""
    conn = sqlite3.connect('roster.db')
    cursor = conn.cursor()

    # SQLite doesn't support ALTER COLUMN, so we need to recreate the table
    print("Creating new assignments table with nullable solution_id...")

    # Create new table with nullable solution_id
    cursor.execute("""
        CREATE TABLE assignments_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            solution_id INTEGER,
            event_id TEXT NOT NULL,
            person_id TEXT NOT NULL,
            assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (solution_id) REFERENCES solutions(id),
            FOREIGN KEY (event_id) REFERENCES events(id),
            FOREIGN KEY (person_id) REFERENCES people(id)
        )
    """)

    # Copy data from old table
    cursor.execute("""
        INSERT INTO assignments_new (id, solution_id, event_id, person_id, assigned_at)
        SELECT id, solution_id, event_id, person_id, assigned_at
        FROM assignments
    """)

    # Drop old table
    cursor.execute("DROP TABLE assignments")

    # Rename new table
    cursor.execute("ALTER TABLE assignments_new RENAME TO assignments")

    # Recreate indexes
    cursor.execute("CREATE INDEX idx_assignments_solution_id ON assignments(solution_id)")
    cursor.execute("CREATE INDEX idx_assignments_event_id ON assignments(event_id)")
    cursor.execute("CREATE INDEX idx_assignments_person_id ON assignments(person_id)")

    conn.commit()
    conn.close()
    print("✅ Migration complete! solution_id is now nullable.")

if __name__ == "__main__":
    migrate()
