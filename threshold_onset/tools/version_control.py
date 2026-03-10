"""
Local Version Control System

Architecture:
  watchfiles (file monitoring)
    ↓
  content hash (hashlib)
    ↓
  diff / snapshot
    ↓
  local version store (sqlite + files)
"""

import hashlib
import sqlite3
import os
import json
from datetime import datetime
from pathlib import Path
from difflib import unified_diff
from watchfiles import watch


class LocalVersionControl:
    def __init__(self, root_dir=".", db_path=".versions.db", versions_dir="versions"):
        self.root_dir = Path(root_dir).resolve()
        self.db_path = self.root_dir / db_path
        self.versions_dir = self.root_dir / versions_dir
        self.versions_dir.mkdir(exist_ok=True)
        
        # Tracked paths (relative to root)
        self.tracked_paths = [
            "src/",                       # All source code
            "docs/",                      # All documentation
            "README.md",                  # Project overview
        ]
        
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite database for version metadata."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                file_path TEXT NOT NULL,
                content_hash TEXT NOT NULL,
                snapshot_path TEXT,
                parent_hash TEXT,
                UNIQUE(file_path, content_hash)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS file_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                snapshot_id INTEGER,
                file_path TEXT NOT NULL,
                old_hash TEXT,
                new_hash TEXT,
                diff_path TEXT,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (snapshot_id) REFERENCES snapshots(id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def _hash_content(self, content):
        """Compute SHA256 hash of content."""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def _get_file_hash(self, file_path):
        """Get hash of file content."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return self._hash_content(content)
        except Exception:
            return None
    
    def _get_last_hash(self, file_path):
        """Get last known hash for a file from database."""
        # Normalize file path for consistent storage
        file_path_str = str(Path(file_path).relative_to(self.root_dir)) if Path(file_path).is_absolute() else str(file_path)
        file_path_str = file_path_str.replace('\\', '/')
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT content_hash FROM snapshots
                WHERE file_path = ?
                ORDER BY id DESC
                LIMIT 1
            """, (file_path_str,))
            
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result else None
        except sqlite3.Error as e:
            print(f"[VERSION] Database error in _get_last_hash: {e}")
            return None
    
    def _store_snapshot(self, file_path, content_hash, content):
        """Store file snapshot and return snapshot ID."""
        # Normalize file path for consistent storage
        file_path_obj = Path(file_path)
        if file_path_obj.is_absolute():
            file_path_str = str(file_path_obj.relative_to(self.root_dir))
        else:
            file_path_str = str(file_path_obj)
        file_path_str = file_path_str.replace('\\', '/')
        
        timestamp = datetime.now().isoformat()
        snapshot_path = self.versions_dir / f"{content_hash[:12]}_{file_path_obj.name}"
        
        try:
            # Store file content
            snapshot_path.parent.mkdir(parents=True, exist_ok=True)
            with open(snapshot_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except (IOError, OSError) as e:
            print(f"[VERSION] Error writing snapshot {snapshot_path}: {e}")
            return None
        
        try:
            # Store metadata in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get parent hash
            parent_hash = self._get_last_hash(file_path)
            
            cursor.execute("""
                INSERT INTO snapshots (timestamp, file_path, content_hash, snapshot_path, parent_hash)
                VALUES (?, ?, ?, ?, ?)
            """, (timestamp, file_path_str, content_hash, str(snapshot_path), parent_hash))
            
            snapshot_id = cursor.lastrowid
            
            # Store diff if parent exists
            if parent_hash:
                old_content = self._get_snapshot_content(parent_hash, file_path)
                if old_content:
                    diff = self._compute_diff(old_content, content)
                    diff_path = self.versions_dir / f"{content_hash[:12]}_{file_path_obj.name}.diff"
                    try:
                        with open(diff_path, 'w', encoding='utf-8') as f:
                            f.write(diff)
                    except (IOError, OSError) as e:
                        print(f"[VERSION] Error writing diff {diff_path}: {e}")
                    
                    cursor.execute("""
                        INSERT INTO file_history (snapshot_id, file_path, old_hash, new_hash, diff_path, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (snapshot_id, file_path_str, parent_hash, content_hash, str(diff_path), timestamp))
            
            conn.commit()
            conn.close()
            
            return snapshot_id
        except sqlite3.Error as e:
            print(f"[VERSION] Database error in _store_snapshot: {e}")
            return None
    
    def _get_snapshot_content(self, content_hash, file_path):
        """Retrieve content from snapshot by hash."""
        snapshot_path = self.versions_dir / f"{content_hash[:12]}_{Path(file_path).name}"
        try:
            with open(snapshot_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            return None
    
    def _compute_diff(self, old_content, new_content):
        """Compute unified diff between old and new content."""
        old_lines = old_content.splitlines(keepends=True)
        new_lines = new_content.splitlines(keepends=True)
        diff = unified_diff(old_lines, new_lines, fromfile='old', tofile='new', lineterm='')
        return ''.join(diff)
    
    def _is_tracked(self, file_path):
        """Check if file path should be tracked."""
        file_path = Path(file_path)
        
        # Convert to relative path from root
        try:
            if file_path.is_absolute():
                rel_path = file_path.relative_to(self.root_dir)
            else:
                rel_path = file_path
        except ValueError:
            # Path is not relative to root, skip
            return False
        
        rel_path_str = str(rel_path).replace('\\', '/')  # Normalize path separators
        
        for tracked in self.tracked_paths:
            tracked_normalized = tracked.replace('\\', '/')
            if rel_path_str.startswith(tracked_normalized) or rel_path_str == tracked_normalized:
                return True
        return False
    
    def _handle_change(self, file_path):
        """Handle file change event."""
        file_path = Path(file_path)
        
        if not file_path.exists() or not file_path.is_file():
            return
        
        # Ensure absolute path for tracking check
        if not file_path.is_absolute():
            file_path = (self.root_dir / file_path).resolve()
        
        if not self._is_tracked(file_path):
            return
        
        # Get current hash
        current_hash = self._get_file_hash(file_path)
        if not current_hash:
            return
        
        # Check if changed
        last_hash = self._get_last_hash(file_path)
        if current_hash == last_hash:
            return  # No change
        
        # Store snapshot
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except (UnicodeDecodeError, PermissionError, IOError) as e:
            print(f"[VERSION] Error reading {file_path}: {e}")
            return
        
        snapshot_id = self._store_snapshot(file_path, current_hash, content)
        
        print(f"[VERSION] Snapshot {snapshot_id}: {file_path} (hash: {current_hash[:12]}...)")
    
    def watch(self):
        """Start watching for file changes."""
        print(f"[VERSION] Watching: {self.root_dir}")
        print(f"[VERSION] Tracking: {self.tracked_paths}")
        print(f"[VERSION] Database: {self.db_path}")
        print("[VERSION] Press Ctrl+C to stop\n")
        
        # Watch tracked paths
        watch_paths = [self.root_dir / path for path in self.tracked_paths]
        
        for changes in watch(*watch_paths):
            for change in changes:
                change_type, file_path = change
                if change_type.name in ['MODIFIED', 'CREATED']:
                    self._handle_change(file_path)
    
    def get_history(self, file_path=None, limit=10):
        """Get version history for file(s)."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if file_path:
                # Normalize file path
                file_path_str = str(Path(file_path).relative_to(self.root_dir)) if Path(file_path).is_absolute() else str(file_path)
                file_path_str = file_path_str.replace('\\', '/')
                
                cursor.execute("""
                    SELECT id, timestamp, file_path, content_hash, parent_hash
                    FROM snapshots
                    WHERE file_path = ?
                    ORDER BY id DESC
                    LIMIT ?
                """, (file_path_str, limit))
            else:
                cursor.execute("""
                    SELECT id, timestamp, file_path, content_hash, parent_hash
                    FROM snapshots
                    ORDER BY id DESC
                    LIMIT ?
                """, (limit,))
            
            results = cursor.fetchall()
            conn.close()
            
            return results
        except sqlite3.Error as e:
            print(f"[VERSION] Database error in get_history: {e}")
            return []


if __name__ == "__main__":
    vc = LocalVersionControl()
    
    try:
        vc.watch()
    except KeyboardInterrupt:
        print("\n[VERSION] Stopped watching")
