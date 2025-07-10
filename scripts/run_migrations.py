#!/usr/bin/env python3
"""
Database Migration Runner for Restaurant AI Platform
Runs database migrations in the correct order for both local and Render deployment
"""
import os
import sys
import psycopg2
import logging
from pathlib import Path
from typing import List, Tuple
import json
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MigrationRunner:
    def __init__(self, database_url: str = None):
        """Initialize migration runner with database connection"""
        self.database_url = database_url or os.getenv('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable is required")
        
        # Path to migrations directory
        self.migrations_dir = Path(__file__).parent.parent / 'backend' / 'shared' / 'database' / 'migrations'
        
        # Ensure migrations directory exists
        self.migrations_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Migration runner initialized for: {self.migrations_dir}")
    
    def get_db_connection(self):
        """Get database connection"""
        try:
            conn = psycopg2.connect(self.database_url)
            return conn
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def create_migrations_table(self, conn):
        """Create migrations tracking table if it doesn't exist"""
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS schema_migrations (
                        id SERIAL PRIMARY KEY,
                        version VARCHAR(255) UNIQUE NOT NULL,
                        name VARCHAR(255) NOT NULL,
                        checksum VARCHAR(64),
                        applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        applied_by VARCHAR(100) DEFAULT current_user,
                        execution_time_ms INTEGER
                    );
                """)
                
                # Create index for faster lookups
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_schema_migrations_version 
                    ON schema_migrations(version);
                """)
                
                conn.commit()
                logger.info("Schema migrations table created/verified")
        except Exception as e:
            logger.error(f"Failed to create migrations table: {e}")
            conn.rollback()
            raise
    
    def get_applied_migrations(self, conn) -> List[str]:
        """Get list of already applied migrations"""
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT version FROM schema_migrations ORDER BY version")
                return [row[0] for row in cur.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get applied migrations: {e}")
            return []
    
    def get_migration_files(self) -> List[Tuple[str, Path]]:
        """Get list of migration files in order"""
        migration_files = []
        
        for file_path in sorted(self.migrations_dir.glob('*.sql')):
            # Extract version from filename (e.g., 001_add_ai_configuration.sql -> 001)
            version = file_path.stem.split('_')[0]
            migration_files.append((version, file_path))
        
        return migration_files
    
    def calculate_checksum(self, file_path: Path) -> str:
        """Calculate MD5 checksum of migration file"""
        import hashlib
        
        with open(file_path, 'rb') as f:
            content = f.read()
            return hashlib.md5(content).hexdigest()
    
    def execute_migration(self, conn, version: str, file_path: Path) -> bool:
        """Execute a single migration file"""
        try:
            logger.info(f"Executing migration {version}: {file_path.name}")
            
            # Read migration file
            with open(file_path, 'r', encoding='utf-8') as f:
                migration_sql = f.read()
            
            start_time = datetime.now()
            
            with conn.cursor() as cur:
                # Execute migration
                cur.execute(migration_sql)
                
                # Calculate execution time
                execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
                
                # Record migration in tracking table
                checksum = self.calculate_checksum(file_path)
                cur.execute("""
                    INSERT INTO schema_migrations (version, name, checksum, execution_time_ms)
                    VALUES (%s, %s, %s, %s)
                """, (version, file_path.stem, checksum, execution_time))
                
                conn.commit()
                logger.info(f"Migration {version} completed successfully in {execution_time}ms")
                return True
                
        except Exception as e:
            logger.error(f"Failed to execute migration {version}: {e}")
            conn.rollback()
            return False
    
    def run_migrations(self, dry_run: bool = False) -> bool:
        """Run all pending migrations"""
        try:
            logger.info("Starting database migrations...")
            
            if dry_run:
                logger.info("DRY RUN MODE - No changes will be made")
            
            # Get database connection
            conn = self.get_db_connection()
            
            # Create migrations tracking table
            if not dry_run:
                self.create_migrations_table(conn)
            
            # Get applied migrations
            applied_migrations = self.get_applied_migrations(conn) if not dry_run else []
            logger.info(f"Applied migrations: {applied_migrations}")
            
            # Get migration files
            migration_files = self.get_migration_files()
            logger.info(f"Found {len(migration_files)} migration files")
            
            # Execute pending migrations
            pending_migrations = [
                (version, file_path) for version, file_path in migration_files
                if version not in applied_migrations
            ]
            
            if not pending_migrations:
                logger.info("No pending migrations found")
                return True
            
            logger.info(f"Found {len(pending_migrations)} pending migrations")
            
            for version, file_path in pending_migrations:
                if dry_run:
                    logger.info(f"Would execute migration {version}: {file_path.name}")
                    continue
                
                success = self.execute_migration(conn, version, file_path)
                if not success:
                    logger.error(f"Migration {version} failed - stopping execution")
                    return False
            
            conn.close()
            
            if not dry_run:
                logger.info("All migrations completed successfully")
            else:
                logger.info("Dry run completed successfully")
            
            return True
            
        except Exception as e:
            logger.error(f"Migration runner failed: {e}")
            return False
    
    def rollback_migration(self, version: str) -> bool:
        """Rollback a specific migration (if rollback file exists)"""
        try:
            rollback_file = self.migrations_dir / f"{version}_rollback.sql"
            
            if not rollback_file.exists():
                logger.error(f"Rollback file not found: {rollback_file}")
                return False
            
            logger.info(f"Rolling back migration {version}")
            
            conn = self.get_db_connection()
            
            with open(rollback_file, 'r', encoding='utf-8') as f:
                rollback_sql = f.read()
            
            with conn.cursor() as cur:
                cur.execute(rollback_sql)
                
                # Remove from migrations table
                cur.execute("""
                    DELETE FROM schema_migrations WHERE version = %s
                """, (version,))
                
                conn.commit()
                
            conn.close()
            logger.info(f"Migration {version} rolled back successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to rollback migration {version}: {e}")
            return False
    
    def get_migration_status(self) -> dict:
        """Get status of all migrations"""
        try:
            conn = self.get_db_connection()
            applied_migrations = self.get_applied_migrations(conn)
            migration_files = self.get_migration_files()
            
            status = {
                'total_migrations': len(migration_files),
                'applied_migrations': len(applied_migrations),
                'pending_migrations': len(migration_files) - len(applied_migrations),
                'migrations': []
            }
            
            for version, file_path in migration_files:
                migration_info = {
                    'version': version,
                    'name': file_path.stem,
                    'applied': version in applied_migrations,
                    'file_path': str(file_path)
                }
                status['migrations'].append(migration_info)
            
            conn.close()
            return status
            
        except Exception as e:
            logger.error(f"Failed to get migration status: {e}")
            return {'error': str(e)}

def main():
    """Main entry point for migration runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Database Migration Runner')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Show what would be migrated without making changes')
    parser.add_argument('--status', action='store_true',
                       help='Show migration status')
    parser.add_argument('--rollback', type=str, metavar='VERSION',
                       help='Rollback specific migration version')
    parser.add_argument('--database-url', type=str,
                       help='Database URL (overrides DATABASE_URL env var)')
    
    args = parser.parse_args()
    
    try:
        runner = MigrationRunner(database_url=args.database_url)
        
        if args.status:
            status = runner.get_migration_status()
            print(json.dumps(status, indent=2))
            return
        
        if args.rollback:
            success = runner.rollback_migration(args.rollback)
            sys.exit(0 if success else 1)
        
        # Run migrations
        success = runner.run_migrations(dry_run=args.dry_run)
        sys.exit(0 if success else 1)
        
    except Exception as e:
        logger.error(f"Migration runner error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()