#!/bin/bash
# Deploy to Render: Export local data and import to Render database

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

# Check if RENDER_DATABASE_URL is set
if [ -z "$RENDER_DATABASE_URL" ]; then
    log_error "RENDER_DATABASE_URL environment variable is not set!"
    echo "Please set it with:"
    echo "export RENDER_DATABASE_URL='postgresql://user:pass@host:port/db'"
    exit 1
fi

# Default values
RESTAURANT_SLUG=""
BACKUP_DIR="./backups"
EXPORT_FILE=""
SKIP_EXPORT=false
SKIP_COMPARISON=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -r|--restaurant)
            RESTAURANT_SLUG="$2"
            shift 2
            ;;
        -b|--backup-dir)
            BACKUP_DIR="$2"
            shift 2
            ;;
        -f|--file)
            EXPORT_FILE="$2"
            SKIP_EXPORT=true
            shift 2
            ;;
        --skip-export)
            SKIP_EXPORT=true
            shift
            ;;
        --skip-comparison)
            SKIP_COMPARISON=true
            shift
            ;;
        -h|--help)
            echo "Deploy to Render Script"
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  -r, --restaurant SLUG    Export specific restaurant (default: all)"
            echo "  -b, --backup-dir DIR     Backup directory (default: ./backups)"
            echo "  -f, --file FILE          Use existing export file (skips export)"
            echo "  --skip-export            Skip export step"
            echo "  --skip-comparison        Skip final comparison"
            echo "  -h, --help               Show this help"
            echo ""
            echo "Examples:"
            echo "  $0                                    # Deploy all restaurants"
            echo "  $0 -r chip-cookies                   # Deploy specific restaurant"
            echo "  $0 -f backup.json                    # Use existing export file"
            echo "  $0 --skip-comparison                 # Skip final verification"
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            echo "Use -h or --help for usage information"
            exit 1
            ;;
    esac
done

log_info "🚀 Starting Render deployment process..."

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Step 1: Export data (unless skipped)
if [ "$SKIP_EXPORT" = false ]; then
    log_info "📤 Exporting data from local database..."
    
    if [ -n "$RESTAURANT_SLUG" ]; then
        # Export specific restaurant
        log_info "Exporting restaurant: $RESTAURANT_SLUG"
        python3 scripts/database/export.py --restaurant "$RESTAURANT_SLUG" --output-dir "$BACKUP_DIR"
        
        # Find the latest export file for this restaurant
        EXPORT_FILE=$(ls -t "$BACKUP_DIR"/${RESTAURANT_SLUG//-/_}_export_*.json 2>/dev/null | head -1)
    else
        # Export all restaurants
        log_info "Exporting all restaurants"
        python3 scripts/database/export.py --output-dir "$BACKUP_DIR"
        
        # Find the latest export file
        EXPORT_FILE=$(ls -t "$BACKUP_DIR"/all_restaurants_export_*.json 2>/dev/null | head -1)
    fi
    
    if [ -z "$EXPORT_FILE" ] || [ ! -f "$EXPORT_FILE" ]; then
        log_error "Export failed - no export file found!"
        exit 1
    fi
    
    log_success "Export completed: $EXPORT_FILE"
else
    log_info "📁 Using existing export file: $EXPORT_FILE"
    
    if [ ! -f "$EXPORT_FILE" ]; then
        log_error "Export file not found: $EXPORT_FILE"
        exit 1
    fi
fi

# Step 2: Import to Render database
log_info "📥 Importing data to Render database..."

if python3 scripts/database/import.py "$EXPORT_FILE" --target remote; then
    log_success "Import to Render completed successfully!"
else
    log_error "Import to Render failed!"
    exit 1
fi

# Step 3: Verify with comparison (unless skipped)
if [ "$SKIP_COMPARISON" = false ]; then
    log_info "🔍 Verifying data consistency..."
    
    if [ -n "$RESTAURANT_SLUG" ]; then
        # Compare specific restaurant
        if python3 scripts/database/compare.py --restaurants "$RESTAURANT_SLUG"; then
            log_success "✨ Data verification passed! Local and Render databases are identical."
        else
            log_warning "Data verification found differences. Check the output above."
            exit 1
        fi
    else
        # Compare all restaurants
        if python3 scripts/database/compare.py; then
            log_success "✨ Data verification passed! Local and Render databases are identical."
        else
            log_warning "Data verification found differences. Check the output above."
            exit 1
        fi
    fi
else
    log_info "⏭️  Skipping data verification"
fi

# Success message
echo ""
log_success "🎉 Render deployment completed successfully!"
echo ""
log_info "📋 Summary:"
echo "  • Export file: $EXPORT_FILE"
echo "  • Target: Render database"
if [ "$SKIP_COMPARISON" = false ]; then
    echo "  • Verification: ✅ Passed"
else
    echo "  • Verification: ⏭️  Skipped"
fi
echo ""
log_info "🌐 Your application is now ready to deploy to Render with the updated data!"