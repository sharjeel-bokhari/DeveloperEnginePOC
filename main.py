# Entry point: Safely integrates the agent and terminal manager

import sys
import time
import os
import traceback
import argparse
from agents.openAiLLM import OpenAIClient
from managers.OpenAiTerminalManager import OPENAITerminalManager

def main(working_dir: str):
    try:
        # Initialize agent and terminal manager
        client = OpenAIClient()
        terminal_manager = OPENAITerminalManager(working_dir=working_dir)

        print("Initializing Agent and Terminal Manager...")

        # Link them together
        client.set_terminal_manager(terminal_manager)
        terminal_manager.set_llm(client)

        # Initialize terminal with timeout
        MAX_INIT_WAIT = 10  # Maximum seconds to wait for initialization
        start_time = time.time()
        
        terminal_manager._open_new_terminal()
        
        # Wait for terminal to be ready
        while not terminal_manager._is_terminal_alive():
            if time.time() - start_time > MAX_INIT_WAIT:
                raise RuntimeError("Terminal failed to initialize within timeout period")
            time.sleep(0.5)

        print("Agent and Terminal Manager initialized successfully.")
        print(f"Terminal ready at: {terminal_manager.get_terminal_cwd()}")
        
        # Example interaction loop (simple CLI)
        while True:
            try:
                user_input = input("\n[Agent] Enter your request (or 'exit' to quit): ").strip()
                if user_input.lower() in {"exit", "quit"}:
                    print("Exiting. Goodbye!")
                    break
                
                output = client.process_user_prompt(user_input)
                print("[Agent Output]:", output)
            except KeyboardInterrupt:
                print("\nReceived interrupt signal. Cleaning up...")
                break
            except Exception as e:
                print("[Error]:", str(e))
                traceback.print_exc()

    except Exception as e:
        print("[Fatal Error]:", str(e))
        traceback.print_exc()
        return 1

    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='AI Agent for Code Generation and Management')
    parser.add_argument('--path', '-p', 
                       type=str,
                       help='Starting directory path for the agent',
                       default=os.getcwd())
    
    args = parser.parse_args()
    # Fix: Only expand and normalize path once
    working_dir = os.path.abspath(os.path.expanduser(args.path))

    # Validate directory
    if not os.path.exists(working_dir):
        print(f"[Error]: The specified path '{working_dir}' does not exist.")
        sys.exit(1)
    if not os.path.isdir(working_dir):
        print(f"[Error]: The specified path '{working_dir}' is not a directory.")
        sys.exit(1)
    if not os.access(working_dir, os.W_OK):
        print(f"[Error]: The specified path '{working_dir}' is not writable.")
        sys.exit(1)

    print(f"Starting agent with working directory: {working_dir}")
    sys.exit(main(working_dir=working_dir))

