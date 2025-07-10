# Database Management Scripts

This directory contains reusable scripts for managing restaurant data across different environments.

## Scripts Overview

### 🔄 `export.py` - Data Export
Export restaurant data from any database to portable JSON format.

**Basic Usage:**
```bash
# Export specific restaurant
python scripts/database/export.py --restaurant chip-cookies

# Export all restaurants
python scripts/database/export.py

# List available restaurants
python scripts/database/export.py --list

# Export to specific directory
python scripts/database/export.py --restaurant chip-cookies --output-dir ./backups

# Include inactive items
python scripts/database/export.py --restaurant chip-cookies --include-inactive
```

**Advanced Usage:**
```bash
# Custom filename
python scripts/database/export.py --restaurant chip-cookies --filename my_backup.json

# Export all with custom settings
python scripts/database/export.py --output-dir ./exports --include-inactive
```

### 📥 `import.py` - Data Import
Import restaurant data to local or remote databases with smart overwrite handling.

**Local Database Import:**
```bash
# Import to local database
python scripts/database/import.py restaurant_backup.json

# Specify target explicitly
python scripts/database/import.py restaurant_backup.json --target local
```

**Remote Database Import:**
```bash
# Import to remote database
python scripts/database/import.py restaurant_backup.json --target remote --database-url "postgresql://user:pass@host:port/db"

# Use environment variable
export DATABASE_URL="postgresql://user:pass@host:port/db"
python scripts/database/import.py restaurant_backup.json --target remote

# For Render specifically
export RENDER_DATABASE_URL="postgresql://user:pass@host:port/db"
python scripts/database/import.py restaurant_backup.json --target remote
```

### 🔍 `compare.py` - Database Comparison
Compare data between local and remote databases to verify consistency.

**Basic Comparison:**
```bash
# Compare local vs remote (default)
export RENDER_DATABASE_URL="postgresql://user:pass@host:port/db"
python scripts/database/compare.py

# Compare specific restaurants
python scripts/database/compare.py --restaurants chip-cookies mario-pizza

# Compare two remote databases
python scripts/database/compare.py --source remote --target remote \
  --source-url "postgresql://..." --target-url "postgresql://..."
```

**Advanced Comparison:**
```bash
# Verbose output
python scripts/database/compare.py --verbose

# Compare local to local (useful for testing)
python scripts/database/compare.py --source local --target local
```

## Common Workflows

### 🚀 **Deploying to Render**
```bash
# 1. Export your local data
python scripts/database/export.py --restaurant chip-cookies

# 2. Import to Render
export RENDER_DATABASE_URL="your_render_database_url"
python scripts/database/import.py chip_cookies_export_*.json --target remote

# 3. Verify the import
python scripts/database/compare.py
```

### 💾 **Creating Backups**
```bash
# Create timestamped backup of all restaurants
python scripts/database/export.py --output-dir ./backups

# Create backup of specific restaurant
python scripts/database/export.py --restaurant chip-cookies --output-dir ./backups
```

### 🔄 **Migrating Between Environments**
```bash
# Export from production
python scripts/database/export.py --all --output-dir ./migration

# Import to staging
python scripts/database/import.py ./migration/all_restaurants_*.json --target remote --database-url "staging_url"

# Verify migration
python scripts/database/compare.py --source remote --target remote \
  --source-url "production_url" --target-url "staging_url"
```

### 🧪 **Development Workflows**
```bash
# Reset local database with production data
python scripts/database/export.py --restaurant chip-cookies --output-dir ./temp
python scripts/database/import.py ./temp/chip_cookies_*.json --target local

# Test changes locally then deploy
python scripts/database/export.py --restaurant chip-cookies
# ... make changes locally ...
python scripts/database/import.py chip_cookies_*.json --target remote
python scripts/database/compare.py  # Verify consistency
```

## Environment Variables

The scripts support these environment variables:

- `DATABASE_URL` - Generic database URL for imports
- `RENDER_DATABASE_URL` - Render-specific database URL
- `SOURCE_DATABASE_URL` - Source database for comparisons
- `TARGET_DATABASE_URL` - Target database for comparisons

## File Formats

### Export Format v2.0
```json
{
  "version": "2.0",
  "exported_at": "2025-01-01T12:00:00",
  "metadata": {
    "restaurant_slug": "chip-cookies",
    "include_inactive": false,
    "exporter": "restaurant-ai-platform"
  },
  "restaurant": {
    "name": "Chip Cookies",
    "slug": "chip-cookies",
    "cuisine_type": "Dessert",
    "description": "...",
    "avatar_config": {...},
    "theme_config": {...},
    "contact_info": {...},
    "settings": {...},
    "is_active": true
  },
  "categories": [...],
  "items": [...],
  "ingredients": [...]
}
```

### Multi-Restaurant Format
```json
{
  "version": "2.0",
  "exported_at": "2025-01-01T12:00:00",
  "metadata": {
    "export_type": "all_restaurants",
    "include_inactive": false,
    "exporter": "restaurant-ai-platform"
  },
  "restaurants": [
    {
      "restaurant": {...},
      "categories": [...],
      "items": [...],
      "ingredients": [...]
    }
  ]
}
```

## Error Handling

All scripts include comprehensive error handling:

- **Connection errors** - Clear messages about database connectivity
- **Data validation** - Checks for required fields and data integrity
- **Conflict resolution** - Smart handling of existing data during imports
- **Rollback support** - Transactions ensure data consistency

## Dependencies

### Local Database Operations
- SQLAlchemy
- PostgreSQL driver
- Your application's database models

### Remote Database Operations
- `psycopg2-binary` for PostgreSQL connections

### Installation
```bash
pip install psycopg2-binary  # For remote database operations
```

## Tips

1. **Always backup before importing** - Run exports before major changes
2. **Use comparisons to verify** - Always compare after migrations
3. **Test with dry-run first** - Use `--dry-run` flag when available
4. **Set environment variables** - Makes repeated operations easier
5. **Use specific restaurant slugs** - Faster than full database operations
6. **Check file permissions** - Ensure output directories are writable

## Troubleshooting

### Common Issues

**"Restaurant not found"**
- Check the slug spelling
- Use `--list` to see available restaurants
- Ensure the restaurant is active (or use `--include-inactive`)

**"Database connection failed"**
- Verify the database URL format
- Check network connectivity
- Ensure database credentials are correct

**"Permission denied"**
- Check file/directory permissions
- Ensure database user has required permissions
- Verify environment variables are set correctly

**"Data mismatch during comparison"**
- Check if data was modified between export/import
- Verify both databases are using the same schema version
- Look at specific error messages for field-level issues