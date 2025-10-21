"""Script to seed Supabase database with regulatory data"""

import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.supabase_client import SupabaseClient
from app.data.loader import RegulatoryDataLoader

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


def clear_tables():
    """
    Clear all regulatory data tables in Supabase.
    
    Tables cleared:
    - mandatory_fields
    - forbidden_phrases
    - regulatory_acts
    - allowed_substances
    """
    client = SupabaseClient().client
    tables = ["mandatory_fields", "forbidden_phrases", "regulatory_acts", "allowed_substances"]
    
    logger.info("🗑️  Clearing tables...")
    
    for table in tables:
        try:
            # Delete all records (neq ensures we get all records)
            result = client.table(table).delete().neq('id', 0).execute()
            logger.info(f"   ✓ Cleared table: {table}")
        except Exception as e:
            logger.warning(f"   ⚠️  Could not clear {table}: {e}")
            # Table might not exist yet, which is fine
    
    logger.info("✅ Tables cleared\n")


def seed_mandatory_fields():
    """
    Seed mandatory fields table with 18 regulatory requirements.
    
    Returns:
        int: Number of records inserted
    """
    client = SupabaseClient().client
    logger.info("📋 Seeding mandatory_fields...")
    
    # Load data from JSON
    fields = RegulatoryDataLoader.load_mandatory_fields()
    
    inserted_count = 0
    failed_count = 0
    
    # Use tqdm for progress bar
    for field in tqdm(fields, desc="Mandatory Fields", unit="field"):
        try:
            # Remove 'id' field - Supabase will auto-generate
            field_data = {k: v for k, v in field.items() if k != 'id'}
            
            # Insert into Supabase
            client.table("mandatory_fields").insert(field_data).execute()
            inserted_count += 1
            
        except Exception as e:
            logger.error(f"   ❌ Failed to insert field {field.get('field_name')}: {e}")
            failed_count += 1
    
    logger.info(f"✅ Inserted {inserted_count} mandatory fields ({failed_count} failed)\n")
    return inserted_count


def seed_forbidden_phrases():
    """
    Seed forbidden phrases table with 52 prohibited marketing claims.
    
    Returns:
        int: Number of records inserted
    """
    client = SupabaseClient().client
    logger.info("❌ Seeding forbidden_phrases...")
    
    # Load data from JSON
    phrases = RegulatoryDataLoader.load_forbidden_phrases()
    
    inserted_count = 0
    failed_count = 0
    
    # Use tqdm for progress bar
    for phrase in tqdm(phrases, desc="Forbidden Phrases", unit="phrase"):
        try:
            # Remove 'id' field - Supabase will auto-generate
            phrase_data = {k: v for k, v in phrase.items() if k != 'id'}
            
            # Ensure 'variations' is a JSON array (already is from JSON load)
            # PostgreSQL JSONB will handle it automatically
            
            # Insert into Supabase
            client.table("forbidden_phrases").insert(phrase_data).execute()
            inserted_count += 1
            
        except Exception as e:
            logger.error(f"   ❌ Failed to insert phrase '{phrase.get('phrase')}': {e}")
            failed_count += 1
    
    logger.info(f"✅ Inserted {inserted_count} forbidden phrases ({failed_count} failed)\n")
    return inserted_count


def seed_regulatory_acts():
    """
    Seed regulatory acts table with 4 Ukrainian laws and orders.
    
    Returns:
        int: Number of records inserted
    """
    client = SupabaseClient().client
    logger.info("🏛️  Seeding regulatory_acts...")
    
    # Load data from JSON
    acts = RegulatoryDataLoader.load_regulatory_acts()
    
    inserted_count = 0
    failed_count = 0
    
    # Use tqdm for progress bar
    for act in tqdm(acts, desc="Regulatory Acts", unit="act"):
        try:
            # Prepare data
            act_data = {k: v for k, v in act.items()}
            
            # 'key_requirements' is already an array from JSON
            # PostgreSQL JSONB will handle it automatically
            
            # Insert into Supabase
            client.table("regulatory_acts").insert(act_data).execute()
            inserted_count += 1
            
        except Exception as e:
            logger.error(f"   ❌ Failed to insert act '{act.get('name')}': {e}")
            failed_count += 1
    
    logger.info(f"✅ Inserted {inserted_count} regulatory acts ({failed_count} failed)\n")
    return inserted_count


def seed_allowed_substances():
    """
    Seed allowed substances table with 35 vitamins, minerals, and other substances.
    
    Returns:
        int: Number of records inserted
    """
    client = SupabaseClient().client
    logger.info("💊 Seeding allowed_substances...")
    
    # Load data from JSON
    substances = RegulatoryDataLoader.load_allowed_substances()
    
    inserted_count = 0
    failed_count = 0
    
    # Use tqdm for progress bar
    for substance in tqdm(substances, desc="Allowed Substances", unit="substance"):
        try:
            # Remove 'id' field - Supabase will auto-generate
            substance_data = {k: v for k, v in substance.items() if k != 'id'}
            
            # 'alternative_names' and 'allowed_forms' are already arrays from JSON
            # PostgreSQL JSONB will handle them automatically
            
            # Insert into Supabase
            client.table("allowed_substances").insert(substance_data).execute()
            inserted_count += 1
            
        except Exception as e:
            logger.error(f"   ❌ Failed to insert substance '{substance.get('substance_name')}': {e}")
            failed_count += 1
    
    logger.info(f"✅ Inserted {inserted_count} allowed substances ({failed_count} failed)\n")
    return inserted_count


def verify_seed():
    """
    Verify that all data was seeded correctly by counting records in each table.
    
    Returns:
        dict: Record counts for each table
    """
    client = SupabaseClient().client
    logger.info("🔍 Verifying seed data...")
    
    tables = {
        "mandatory_fields": 18,
        "forbidden_phrases": 52,
        "regulatory_acts": 4,
        "allowed_substances": 35
    }
    
    results = {}
    all_correct = True
    
    for table, expected_count in tables.items():
        try:
            # Count records in table
            result = client.table(table).select("id", count="exact").execute()
            actual_count = result.count if hasattr(result, 'count') else len(result.data)
            results[table] = actual_count
            
            # Check if count matches expected
            if actual_count == expected_count:
                logger.info(f"   ✅ {table}: {actual_count}/{expected_count} records")
            else:
                logger.warning(f"   ⚠️  {table}: {actual_count}/{expected_count} records (MISMATCH)")
                all_correct = False
                
        except Exception as e:
            logger.error(f"   ❌ Error verifying {table}: {e}")
            results[table] = 0
            all_correct = False
    
    if all_correct:
        logger.info("\n✅ All tables verified successfully!")
    else:
        logger.warning("\n⚠️  Some tables have mismatches. Check logs above.")
    
    return results


def print_banner():
    """Print a nice banner for the script"""
    print("\n" + "═" * 80)
    print("║" + " " * 20 + "SUPABASE DATABASE SEEDER" + " " * 34 + "║")
    print("═" * 80)
    print()


def print_summary(results):
    """Print summary of seeding operation"""
    print("\n" + "═" * 80)
    print("║" + " " * 30 + "SUMMARY" + " " * 42 + "║")
    print("═" * 80)
    
    total = sum(results.values())
    
    print(f"\n📊 Total records seeded: {total}")
    print("\nBreakdown:")
    for table, count in results.items():
        print(f"   • {table.replace('_', ' ').title()}: {count}")
    
    print("\n" + "═" * 80)
    print()


def main():
    """
    Main function to seed the database.
    
    Workflow:
    1. Print banner
    2. Ask user if they want to clear tables
    3. Seed all tables with progress bars
    4. Verify seeded data
    5. Print summary
    """
    print_banner()
    
    try:
        # Ask user if they want to clear tables
        clear = input("🗑️  Clear existing tables before seeding? (y/n): ").strip().lower()
        
        if clear == 'y':
            clear_tables()
        else:
            logger.info("⏭️  Skipping table clearing\n")
        
        # Seed all tables
        results = {}
        
        logger.info("🚀 Starting database seed...\n")
        
        results['mandatory_fields'] = seed_mandatory_fields()
        results['forbidden_phrases'] = seed_forbidden_phrases()
        results['regulatory_acts'] = seed_regulatory_acts()
        results['allowed_substances'] = seed_allowed_substances()
        
        # Verify seeded data
        verify_results = verify_seed()
        
        # Print summary
        print_summary(results)
        
        logger.info("✅ Database seeding completed successfully!")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Seeding interrupted by user")
        logger.warning("Database seeding was interrupted")
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"❌ Fatal error during seeding: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
