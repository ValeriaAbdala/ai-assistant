#!/usr/bin/env python3
"""
Script to import existing tickets JSON into database
"""

import json
import sys
import os
import logging
from pathlib import Path
from datetime import datetime

# Add app directory to Python path
sys.path.append(str(Path(__file__).parent))

from app.database.connection import SessionLocal, create_tables
from app.database.models import Ticket

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def find_tickets_json():
    """Find tickets JSON file in the project using intelligent discovery"""
    # First check if tickets directory exists
    tickets_dir = "data/tickets/"
    if not os.path.exists(tickets_dir):
        logger.warning(f"Tickets directory not found: {tickets_dir}")
        return None
    
    # Get all JSON files in tickets directory
    try:
        json_files = [f for f in os.listdir(tickets_dir) if f.endswith('.json')]
        
        if not json_files:
            logger.warning(f"No JSON files found in {tickets_dir}")
            return None
        
        if len(json_files) == 1:
            # Perfect - only one JSON file, use it
            found_file = os.path.join(tickets_dir, json_files[0])
            logger.info(f"Auto-discovered tickets file: {found_file}")
            return found_file
        
        # Multiple JSON files - try to pick the best one
        priority_names = ['tickets', 'sample_tickets', 'test_tickets', 'data']
        
        for priority_name in priority_names:
            for json_file in json_files:
                if priority_name in json_file.lower():
                    found_file = os.path.join(tickets_dir, json_file)
                    logger.info(f"Selected tickets file: {found_file} (matched '{priority_name}')")
                    return found_file
        
        # If no priority match, use the first one
        found_file = os.path.join(tickets_dir, json_files[0])
        logger.info(f"Using first available JSON file: {found_file}")
        logger.info(f"Available files were: {', '.join(json_files)}")
        return found_file
        
    except Exception as e:
        logger.error(f"Error scanning tickets directory: {str(e)}")
        return None

def import_tickets_from_json(json_file_path: str = None):
    """Import tickets from JSON file to database"""
    if not json_file_path:
        json_file_path = find_tickets_json()
        
    if not json_file_path:
        logger.error("Could not find tickets JSON file")
        return False
        
    try:
        # First create tables
        create_tables()
        logger.info("Database tables created")
        
        # Read JSON file
        if not os.path.exists(json_file_path):
            logger.error(f"File not found: {json_file_path}")
            return False
            
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        tickets_data = data.get('tickets', [])
        logger.info(f"Found {len(tickets_data)} tickets in JSON")
        
        # Import to database
        db = SessionLocal()
        
        # Check if tickets already exist
        existing_count = db.query(Ticket).count()
        if existing_count > 0:
            logger.info(f"Database already has {existing_count} tickets")
            response = input("Do you want to clear existing tickets and reimport? (y/N): ")
            if response.lower() == 'y':
                db.query(Ticket).delete()
                db.commit()
                logger.info("Existing tickets cleared")
            else:
                logger.info("Import cancelled")
                db.close()
                return False
        
        # Import tickets
        imported_count = 0
        for ticket_data in tickets_data:
            try:
                ticket = Ticket(
                    id=ticket_data.get('id'),
                    title=ticket_data.get('title'),
                    description=ticket_data.get('description'),
                    type=ticket_data.get('type'),
                    severity=ticket_data.get('severity'),
                    priority=ticket_data.get('priority'),
                    status=ticket_data.get('status'),
                    assignee=ticket_data.get('assignee'),
                    reporter=ticket_data.get('reporter'),
                    sprint=ticket_data.get('sprint'),
                    epic=ticket_data.get('epic'),
                    story_points=ticket_data.get('story_points'),
                    affected_customers=ticket_data.get('affected_customers', 0),
                    revenue_impact=float(ticket_data.get('revenue_impact', 0)),
                    business_impact=ticket_data.get('business_impact'),
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                
                db.add(ticket)
                imported_count += 1
                logger.info(f"Imported: {ticket.id} - {ticket.title[:50]}...")
                
            except Exception as e:
                logger.error(f"Error importing ticket {ticket_data.get('id', 'Unknown')}: {str(e)}")
                continue
        
        db.commit()
        db.close()
        
        logger.info(f"Successfully imported {imported_count}/{len(tickets_data)} tickets!")
        logger.info("Database is ready for conversations and analytics")
        
        return True
        
    except Exception as e:
        logger.error(f"Error importing tickets: {str(e)}")
        return False

def verify_import():
    """Verify the import was successful"""
    try:
        db = SessionLocal()
        
        from sqlalchemy import func
        
        tickets = db.query(Ticket).all()
        total_revenue_impact = db.query(func.sum(Ticket.revenue_impact)).scalar() or 0
        
        logger.info(f"\nDATABASE VERIFICATION:")
        logger.info(f"   Total tickets: {len(tickets)}")
        logger.info(f"   Total revenue impact: ${total_revenue_impact:,.2f}")
        
        # Show breakdown by severity
        severities = db.query(Ticket.severity, func.count(Ticket.id)).group_by(Ticket.severity).all()
        logger.info(f"   Breakdown by severity:")
        for severity, count in severities:
            logger.info(f"     {severity}: {count}")
        
        # Show critical tickets
        critical_tickets = db.query(Ticket).filter(Ticket.severity == 'critical').all()
        logger.info(f"\nCRITICAL TICKETS:")
        for ticket in critical_tickets:
            logger.info(f"   {ticket.id}: {ticket.title} (${ticket.revenue_impact:,.0f})")
        
        db.close()
        return True
        
    except Exception as e:
        logger.error(f"Error verifying import: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("Starting ticket import process...")
    
    # Find tickets JSON file using intelligent discovery
    json_file = find_tickets_json()
    
    if not json_file:
        logger.error("Could not find tickets JSON file")
        logger.info("Please ensure a JSON file exists in data/tickets/ directory")
        sys.exit(1)
    
    logger.info(f"Found tickets file: {json_file}")
    
    # Import tickets
    if import_tickets_from_json(json_file):
        logger.info("Import completed successfully!")
        verify_import()
    else:
        logger.error("Import failed!")
        sys.exit(1)