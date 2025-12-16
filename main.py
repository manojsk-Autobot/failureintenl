"""Main entry point for MSSQL Agent."""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import settings
from connectors.mssql import MSSQLConnector
from features.failure_analyzer import FailureAnalyzer
from mail.formatter import EmailFormatter
from mail.sender import EmailSender


async def analyze_and_send(recipient_email: str = None) -> bool:
    """
    Main workflow: Fetch job failure → Analyze → Format → Send email.
    
    Args:
        recipient_email: Email address to send the report to
        
    Returns:
        True if successful, False otherwise
    """
    print("=" * 60)
    print("MSSQL Job Failure Analysis Agent")
    print("=" * 60)
    
    # Step 1: Initialize components
    print("\n📦 Initializing components...")
    db = MSSQLConnector(settings.get_db_config())
    analyzer = FailureAnalyzer()
    formatter = EmailFormatter()
    sender = EmailSender(settings.get_email_config())
    
    # Check if analyzer is ready
    if not analyzer.is_available():
        print("❌ LLM provider not available. Check API key.")
        return False
    
    try:
        # Step 2: Connect to database and fetch data
        print("\n📊 Fetching latest job failure from database...")
        with db:
            job_data = db.fetch_last_row("FailedJobData_Archive")
            if not job_data:
                print("⚠️  No job failures found in database")
                return False
            
            # Use EmailID from database if not provided
            if not recipient_email:
                recipient_email = job_data.get('EmailID') or job_data.get('EmailId') or settings.SENDER_EMAIL
            
            print(f"✓ Found job failure: {job_data.get('JobName', 'Unknown')}")
            print(f"  Server: {job_data.get('ServerName', 'Unknown')}")
            print(f"  Time: {job_data.get('FailedDateTime', 'Unknown')}")
            print(f"  Recipient: {recipient_email}")
        
        # Step 3: Analyze with LLM
        analysis = await analyzer.analyze(job_data)
        if not analysis:
            print("❌ Failed to get analysis from LLM")
            return False
        
        # Step 4: Format email
        print("\n📧 Formatting email...")
        html_body, plain_body = formatter.format_email(analysis, job_data, settings.SENDER_EMAIL)
        print(f"✓ Email formatted ({len(html_body)} characters)")
        
        # Step 5: Send email
        print(f"\n✉️  Sending email to {recipient_email}...")
        subject = f"[URGENT] SQL Job Failure: {job_data.get('JobName', 'Unknown Job')}"
        success = sender.send(
            recipient=recipient_email,
            subject=subject,
            html_body=html_body,
            plain_body=plain_body
        )
        
        if success:
            print("✓ Email sent successfully!")
            print("=" * 60)
            return True
        else:
            print("❌ Failed to send email")
            return False
            
    except Exception as e:
        print(f"❌ Error in workflow: {e}")
        return False


def main():
    """CLI entry point."""
    # Get recipient from command line (optional)
    # If not provided, will use EmailID from database
    recipient = sys.argv[1] if len(sys.argv) > 1 else None
    
    # Run async workflow
    success = asyncio.run(analyze_and_send(recipient))
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
