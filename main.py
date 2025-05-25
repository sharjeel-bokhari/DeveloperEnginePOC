# Entry point: Safely integrates the agent and terminal manager

import sys
import time
import traceback
from agents.openAiLLM import OpenAIClient
from managers.OpenAiTerminalManager import OPENAITerminalManager

def main():
    try:
        # Initialize agent and terminal manager
        client = OpenAIClient()
        terminal_manager = OPENAITerminalManager()

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
    sys.exit(main())

