# Database Management Scripts

Clean, working scripts for managing your restaurant AI platform databases.

## 🔄 **Daily Workflow: Sync Local → Production**

After local development, sync your changes to production:

```bash
# 1. Activate virtual environment
source venv/bin/activate

# 2. Set your Render database URL
export DATABASE_URL="your_render_postgres_url"

# 3. Sync local data to production
python scripts/sync_to_prod.py
```

## 🔍 **Verify Sync & Compare Databases**

Check that local and production match:

```bash
# Quick health checks
python scripts/run_query.py "SELECT COUNT(*) FROM restaurants"
python scripts/run_query.py "SELECT COUNT(*) FROM menu_items"
python scripts/run_query.py "SELECT name FROM restaurants"

# Menu analysis
python scripts/run_query.py "SELECT mc.name as category, COUNT(mi.id) as items FROM menu_categories mc LEFT JOIN menu_items mi ON mc.id = mi.category_id GROUP BY mc.name"
```

## 🏗️ **Initial Setup Scripts**

For first-time setup only:

```bash
# Initialize local database (first time only)
python scripts/init_db.py

# Load Cookie Jar sample data (first time only)  
python scripts/load_cookie_shop.py
```

## 📁 **Script Descriptions**

| Script | Purpose |
|--------|---------|
| `sync_to_prod.py` | **Main sync tool** - syncs local → production |
| `run_query.py` | **Comparison tool** - run queries on both databases |
| `init_db.py` | Initialize database schema |
| `load_cookie_shop.py` | Load Cookie Jar sample data |
| `start_dev.sh` | Start local development services |
| `stop_dev.sh` | Stop local development services |

## ✅ **Your Clean Workflow**

1. **Develop locally** with your local database
2. **Sync to production**: `python scripts/sync_to_prod.py`
3. **Verify it worked**: `python scripts/run_query.py "SELECT COUNT(*) FROM menu_items"`
4. **Done!** 🎉

Simple, reliable, no complex tools needed.