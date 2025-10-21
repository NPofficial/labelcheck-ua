"""Script to update regulatory information from JSON files to database"""

import sys
import logging
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.data.loader import RegulatoryDataLoader
from app.db.supabase_client import SupabaseClient

try:
    from tqdm import tqdm
except ImportError:
    print("Installing tqdm...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "tqdm"])
    from tqdm import tqdm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def check_changes():
    """
    Check for changes between JSON files and database.
    
    Returns:
        dict: Changes detected for each table
    """
    client = SupabaseClient().client
    logger.info("🔍 Checking for changes...")
    
    changes = {
        'mandatory_fields': False,
        'forbidden_phrases': False,
        'regulatory_acts': False,
        'allowed_substances': False
    }
    
    # Check mandatory fields
    json_fields = RegulatoryDataLoader.load_mandatory_fields()
    try:
        db_fields = client.table("mandatory_fields").select("*").execute()
        if len(json_fields) != len(db_fields.data):
            changes['mandatory_fields'] = True
            logger.info(f"   📋 Mandatory fields: {len(json_fields)} in JSON vs {len(db_fields.data)} in DB")
    except:
        changes['mandatory_fields'] = True
        logger.info(f"   📋 Mandatory fields: Table not found or empty")
    
    # Check forbidden phrases
    json_phrases = RegulatoryDataLoader.load_forbidden_phrases()
    try:
        db_phrases = client.table("forbidden_phrases").select("*").execute()
        if len(json_phrases) != len(db_phrases.data):
            changes['forbidden_phrases'] = True
            logger.info(f"   ❌ Forbidden phrases: {len(json_phrases)} in JSON vs {len(db_phrases.data)} in DB")
    except:
        changes['forbidden_phrases'] = True
        logger.info(f"   ❌ Forbidden phrases: Table not found or empty")
    
    # Check regulatory acts
    json_acts = RegulatoryDataLoader.load_regulatory_acts()
    try:
        db_acts = client.table("regulatory_acts").select("*").execute()
        if len(json_acts) != len(db_acts.data):
            changes['regulatory_acts'] = True
            logger.info(f"   🏛️  Regulatory acts: {len(json_acts)} in JSON vs {len(db_acts.data)} in DB")
    except:
        changes['regulatory_acts'] = True
        logger.info(f"   🏛️  Regulatory acts: Table not found or empty")
    
    # Check allowed substances
    json_substances = RegulatoryDataLoader.load_allowed_substances()
    try:
        db_substances = client.table("allowed_substances").select("*").execute()
        if len(json_substances) != len(db_substances.data):
            changes['allowed_substances'] = True
            logger.info(f"   💊 Allowed substances: {len(json_substances)} in JSON vs {len(db_substances.data)} in DB")
    except:
        changes['allowed_substances'] = True
        logger.info(f"   💊 Allowed substances: Table not found or empty")
    
    return changes


def sync_table(table_name: str, loader_method):
    """
    Synchronize a specific table with JSON data.
    
    Args:
        table_name: Name of the table to sync
        loader_method: Method to load data from JSON
        
    Returns:
        tuple: (inserted, updated, deleted) counts
    """
    client = SupabaseClient().client
    logger.info(f"🔄 Syncing {table_name}...")
    
    # Load JSON data
    json_data = loader_method()
    
    # Get existing data from database
    try:
        db_result = client.table(table_name).select("*").execute()
        db_data = {item.get('id'): item for item in db_result.data}
    except:
        db_data = {}
    
    inserted = 0
    updated = 0
    deleted = 0
    
    # Process each JSON record
    for record in tqdm(json_data, desc=f"Syncing {table_name}", unit="record"):
        record_id = record.get('id')
        
        # Remove 'id' for comparison and insert
        record_copy = {k: v for k, v in record.items() if k != 'id'}
        
        try:
            if record_id and record_id in db_data:
                # Record exists - update if changed
                # For now, we'll just skip existing records
                # In production, you'd compare and update if different
                pass
            else:
                # Record doesn't exist - insert
                client.table(table_name).insert(record_copy).execute()
                inserted += 1
                
        except Exception as e:
            logger.error(f"   ❌ Error processing record: {e}")
    
    logger.info(f"   ✅ {table_name}: {inserted} inserted, {updated} updated, {deleted} deleted")
    
    return inserted, updated, deleted


def reload_cache():
    """
    Reload RegulatoryDataLoader cache with fresh data.
    """
    logger.info("♻️  Reloading data cache...")
    RegulatoryDataLoader.clear_cache()
    
    # Force reload
    RegulatoryDataLoader.load_mandatory_fields()
    RegulatoryDataLoader.load_forbidden_phrases()
    RegulatoryDataLoader.load_regulatory_acts()
    RegulatoryDataLoader.load_allowed_substances()
    
    logger.info("   ✅ Cache reloaded")


def print_banner():
    """Print a nice banner for the script"""
    print("\n" + "═" * 80)
    print("║" + " " * 20 + "REGULATORY DATA UPDATER" + " " * 35 + "║")
    print("═" * 80)
    print()


def main():
    """
    Main function to update regulatory data.
    
    Workflow:
    1. Check for changes between JSON and database
    2. If changes detected, ask user to confirm update
    3. Sync changed tables
    4. Reload cache
    5. Print summary
    """
    print_banner()
    
    try:
        # Check for changes
        changes = check_changes()
        
        if not any(changes.values()):
            logger.info("\n✅ All tables are up to date. No changes needed.")
            return
        
        logger.info(f"\n📝 Changes detected in {sum(changes.values())} table(s)")
        
        # Ask for confirmation
        confirm = input("\n🔄 Update database with new data? (y/n): ").strip().lower()
        
        if confirm != 'y':
            logger.info("⏭️  Update cancelled by user")
            return
        
        print()
        
        # Sync changed tables
        results = {}
        
        if changes['mandatory_fields']:
            results['mandatory_fields'] = sync_table(
                'mandatory_fields',
                RegulatoryDataLoader.load_mandatory_fields
            )
        
        if changes['forbidden_phrases']:
            results['forbidden_phrases'] = sync_table(
                'forbidden_phrases',
                RegulatoryDataLoader.load_forbidden_phrases
            )
        
        if changes['regulatory_acts']:
            results['regulatory_acts'] = sync_table(
                'regulatory_acts',
                RegulatoryDataLoader.load_regulatory_acts
            )
        
        if changes['allowed_substances']:
            results['allowed_substances'] = sync_table(
                'allowed_substances',
                RegulatoryDataLoader.load_allowed_substances
            )
        
        # Reload cache
        reload_cache()
        
        # Print summary
        print("\n" + "═" * 80)
        print("║" + " " * 30 + "SUMMARY" + " " * 42 + "║")
        print("═" * 80)
        
        print(f"\n✅ Update completed at {datetime.utcnow().isoformat()}")
        print("\nChanges:")
        
        for table, (inserted, updated, deleted) in results.items():
            if inserted > 0 or updated > 0 or deleted > 0:
                print(f"   • {table.replace('_', ' ').title()}:")
                print(f"      + {inserted} inserted")
                print(f"      ~ {updated} updated")
                print(f"      - {deleted} deleted")
        
        print("\n" + "═" * 80)
        print()
        
        logger.info("✅ Regulatory data update completed successfully!")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Update interrupted by user")
        logger.warning("Regulatory data update was interrupted")
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"❌ Fatal error during update: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
