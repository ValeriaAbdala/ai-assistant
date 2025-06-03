from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.database.models import Base
import logging

logger = logging.getLogger(__name__)

# Create engine
engine = create_engine(
    settings.database_url,
    echo=settings.debug,  # Log SQL queries in debug mode
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Create all tables in the database"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        raise

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_database():
    """Initialize database with tables and sample data"""
    try:
        # Create tables
        create_tables()
        
        # Add sample tickets if database is empty
        db = SessionLocal()
        
        from app.database.models import Ticket
        existing_tickets = db.query(Ticket).count()
        
        if existing_tickets == 0:
            logger.info("Adding sample tickets to database...")
            sample_tickets = [
                Ticket(
                    id="TICKET-001",
                    title="Critical payment gateway timeout",
                    description="Payment processing fails after 30 seconds causing revenue loss",
                    type="bug",
                    severity="critical",
                    priority="high",
                    status="open",
                    assignee="john.doe",
                    reporter="jane.smith",
                    sprint="Sprint 23",
                    epic="Payment System Optimization",
                    story_points=8,
                    affected_customers=1250,
                    revenue_impact=45000.0,
                    business_impact="Direct revenue loss, customer churn risk"
                ),
                Ticket(
                    id="TICKET-002", 
                    title="Mobile app crashes on iOS 17",
                    description="App crashes when accessing user profile on iOS 17 devices",
                    type="bug",
                    severity="high",
                    priority="high", 
                    status="in-progress",
                    assignee="mike.wilson",
                    reporter="sarah.connor",
                    sprint="Sprint 23",
                    epic="Mobile Experience",
                    story_points=5,
                    affected_customers=800,
                    revenue_impact=12000.0,
                    business_impact="User experience degradation"
                ),
                Ticket(
                    id="TICKET-003",
                    title="Database query optimization needed",
                    description="Slow queries affecting dashboard load times",
                    type="performance",
                    severity="medium",
                    priority="medium",
                    status="open",
                    assignee="alex.rodriguez",
                    reporter="david.kim",
                    sprint="Sprint 24",
                    epic="Performance Improvements",
                    story_points=3,
                    affected_customers=2000,
                    revenue_impact=5000.0,
                    business_impact="Reduced user satisfaction"
                ),
                Ticket(
                    id="TICKET-004",
                    title="Add dark mode to dashboard",
                    description="Users requesting dark mode option for better UX",
                    type="feature",
                    severity="low",
                    priority="low",
                    status="open",
                    assignee=None,
                    reporter="lisa.garcia",
                    sprint="Backlog",
                    epic="UI/UX Improvements",
                    story_points=2,
                    affected_customers=0,
                    revenue_impact=0.0,
                    business_impact="Improved user experience"
                ),
                Ticket(
                    id="TICKET-005",
                    title="Security vulnerability in API authentication",
                    description="Potential JWT token bypass allowing unauthorized access",
                    type="security",
                    severity="critical",
                    priority="high",
                    status="in-progress",
                    assignee="security.team",
                    reporter="penetration.test",
                    sprint="Sprint 23",
                    epic="Security Hardening",
                    story_points=13,
                    affected_customers=5000,
                    revenue_impact=100000.0,
                    business_impact="Security breach risk, compliance issues"
                )
            ]
            
            for ticket in sample_tickets:
                db.add(ticket)
            
            db.commit()
            logger.info(f"Added {len(sample_tickets)} sample tickets")
        
        db.close()
        logger.info("Database initialization completed successfully")
        
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise