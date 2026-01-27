
import smtpd
import asyncore
import json
import os
import sys
from datetime import datetime
import signal

# Global file path
LOG_FILE = "mock_smtp_emails.json"

class MockSMTPServer(smtpd.SMTPServer):
    def process_message(self, peer, mailfrom, rcpttos, data, **kwargs):
        print(f"Received email from {mailfrom} to {rcpttos}")
        email_data = {
            "from": mailfrom,
            "to": rcpttos,
            "data": data.decode('utf-8') if isinstance(data, bytes) else str(data),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Read existing
        emails = []
        if os.path.exists(LOG_FILE):
            try:
                with open(LOG_FILE, "r") as f:
                    emails = json.load(f)
            except json.JSONDecodeError:
                pass
        
        emails.append(email_data)
        
        # Write back
        with open(LOG_FILE, "w") as f:
            json.dump(emails, f, indent=2)

def run_server(port):
    # Clear log file on start
    with open(LOG_FILE, "w") as f:
        json.dump([], f)
        
    print(f"Starting Mock SMTP Server on port {port}...")
    server = MockSMTPServer(('127.0.0.1', port), None)
    try:
        asyncore.loop()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 1025
    run_server(port)
