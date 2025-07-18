#!/usr/bin/env python3
"""
Daydreamer Chat Launcher

Easy entry point for the Daydreamer chat interface.
"""

import sys
import os

def main():
    """Launch the appropriate chat interface"""
    print("🧠 Daydreamer Chat Launcher")
    print("=" * 30)
    
    # Check if we're in the right directory
    if not os.path.exists('src'):
        print("❌ Error: Please run this from the daydreamer project root directory")
        print("   (The directory containing the 'src' folder)")
        sys.exit(1)
    
    # Offer chat options
    print("Choose your chat interface:")
    print("1. Research Chat (Full research-grade AI with CoT and daydreaming)")
    print("2. Enhanced Chat (Full DMN system with intrusive thoughts)")
    print("3. Working Chat (Basic conversational AI)")
    print("4. Exit")
    
    while True:
        try:
            choice = input("\nEnter your choice (1-4): ").strip()
            
            if choice == '1':
                print("\n🔬 Launching Research-Grade Daydreamer Chat...")
                try:
                    import research_chat
                    research_chat.main()
                except ImportError as e:
                    print(f"❌ Failed to import research chat: {e}")
                    print("Falling back to enhanced chat...")
                    import enhanced_chat
                    enhanced_chat.main()
                break
            
            elif choice == '2':
                print("\n🚀 Launching Enhanced Daydreamer Chat...")
                try:
                    import enhanced_chat
                    enhanced_chat.main()
                except ImportError as e:
                    print(f"❌ Failed to import enhanced chat: {e}")
                    print("Falling back to working chat...")
                    import working_chat
                    working_chat.main()
                break
                
            elif choice == '3':
                print("\n🚀 Launching Working Daydreamer Chat...")
                import working_chat
                working_chat.main()
                break
                
            elif choice == '4':
                print("👋 Goodbye!")
                break
                
            else:
                print("⚠️  Please enter 1, 2, 3, or 4")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            break

if __name__ == "__main__":
    main()