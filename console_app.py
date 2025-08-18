#!/usr/bin/env python3
"""
Alnitak Console App - Interactive interface for the RAG assistant.
"""

import requests
import json
import sys
import os
from typing import Optional

class AlnitakConsole:
    """
    Console interface for interacting with the Alnitak RAG assistant.
    """
    
    def __init__(self, api_url: str = "http://localhost:5001"):
        """
        Initialize the console app.
        
        Args:
            api_url: URL of the Alnitak API server
        """
        self.api_url = api_url
        self.session = requests.Session()
        
    def check_connection(self) -> bool:
        """Check if the Alnitak server is running."""
        try:
            response = self.session.get(f"{self.api_url}/health", timeout=5)
            if response.status_code == 200:
                return True
            else:
                return False
        except requests.exceptions.RequestException:
            return False
    
    def get_server_info(self) -> Optional[dict]:
        """Get server information."""
        try:
            response = self.session.get(f"{self.api_url}/", timeout=5)
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except requests.exceptions.RequestException:
            return None
    
    def ask_question(self, question: str) -> Optional[str]:
        """
        Ask a question to the RAG assistant.
        
        Args:
            question: The question to ask
            
        Returns:
            The answer from the assistant, or None if there's an error
        """
        try:
            response = self.session.post(
                f"{self.api_url}/ask",
                json={"question": question},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('answer', 'No answer received')
            else:
                return f"Error: {response.status_code} - {response.text}"
                
        except requests.exceptions.Timeout:
            return "Error: Request timed out. The server might be busy."
        except requests.exceptions.RequestException as e:
            return f"Error: Could not connect to server - {str(e)}"
    
    def print_banner(self):
        """Print the Alnitak banner."""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                    🌟 ALNITAK RAG ASSISTANT 🌟                ║
║                                                              ║
║  Your personal AI assistant, grounded in your own knowledge  ║
║                                                              ║
║  Type 'help' for commands, 'quit' to exit                   ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(banner)
    
    def print_help(self):
        """Print help information."""
        help_text = """
📖 Available Commands:
• Type any question to ask Alnitak
• 'help' - Show this help message
• 'status' - Check server status
• 'info' - Show server information
• 'clear' - Clear the screen
• 'quit' or 'exit' - Exit the application

💡 Tips:
• Ask specific questions for better answers
• Questions are answered based on your ingested documents
• If no documents are found, you'll get a helpful message

🔗 API Endpoint: {api_url}
        """.format(api_url=self.api_url)
        print(help_text)
    
    def print_status(self):
        """Print server status."""
        if self.check_connection():
            print("✅ Alnitak server is running and healthy!")
            
            info = self.get_server_info()
            if info:
                print(f"📡 Service: {info.get('service', 'Unknown')}")
                print(f"🌐 Endpoints: {', '.join(info.get('endpoints', {}).keys())}")
        else:
            print("❌ Alnitak server is not responding")
            print("💡 Make sure the server is running with: python3 app.py")
    
    def clear_screen(self):
        """Clear the console screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def run(self):
        """Run the interactive console."""
        self.clear_screen()
        self.print_banner()
        
        # Check initial connection
        if not self.check_connection():
            print("❌ Cannot connect to Alnitak server!")
            print(f"💡 Make sure the server is running on {self.api_url}")
            print("   Start it with: python3 app.py")
            print("\nPress Enter to exit...")
            input()
            return
        
        print("✅ Connected to Alnitak server!")
        print("Type 'help' to see available commands.\n")
        
        while True:
            try:
                # Get user input
                user_input = input("🤔 Ask Alnitak: ").strip()
                
                # Handle commands
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Goodbye! Thanks for using Alnitak!")
                    break
                
                elif user_input.lower() == 'help':
                    self.print_help()
                    continue
                
                elif user_input.lower() == 'status':
                    self.print_status()
                    continue
                
                elif user_input.lower() == 'info':
                    info = self.get_server_info()
                    if info:
                        print("\n📊 Server Information:")
                        print(json.dumps(info, indent=2))
                    else:
                        print("❌ Could not retrieve server information")
                    continue
                
                elif user_input.lower() == 'clear':
                    self.clear_screen()
                    self.print_banner()
                    continue
                
                elif not user_input:
                    continue
                
                # Ask the question
                print("\n🔄 Processing your question...")
                answer = self.ask_question(user_input)
                
                if answer:
                    print(f"\n💬 Alnitak: {answer}")
                else:
                    print("\n❌ No answer received from the server")
                
                print("\n" + "─" * 60 + "\n")
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye! Thanks for using Alnitak!")
                break
            except Exception as e:
                print(f"\n❌ An error occurred: {str(e)}")
                print("Please try again or type 'quit' to exit.\n")

def main():
    """Main function to run the console app."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Alnitak Console App - Interactive RAG Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 console_app.py
  python3 console_app.py --url http://localhost:5001
  python3 console_app.py --url http://192.168.1.100:5001
        """
    )
    
    parser.add_argument(
        '--url', '-u',
        default='http://localhost:5001',
        help='URL of the Alnitak API server (default: http://localhost:5001)'
    )
    
    args = parser.parse_args()
    
    # Create and run the console app
    console = AlnitakConsole(args.url)
    console.run()

if __name__ == '__main__':
    main()
