import os
import sys
import platform
import subprocess
import tempfile
import datetime
import threading
import time
from queue import Queue

class OPENAITerminalManager:
    def __init__(self, working_dir="."):
        self.master_fd = None
        self.child_pid = None
        self.command_history = []
        self.llm = None
        self.interactive_mode = False
        self.input_queue = Queue()
        self.prompt_buffer = ""
        self.monitor_thread = None
        self.lock = threading.Lock()
        self.os_type = platform.system().lower()
        self.script_path = None
        self.process = None
        self.command_completed = threading.Event()
        self.output_buffer = ""
        self.working_dir = os.path.abspath(working_dir)
    
    def set_llm(self, llm):
        self.llm = llm
    def health_check(self):
        if self.child_pid is None:
            raise RuntimeError("No terminal session is currently active.")
        try:
            os.kill(self.child_pid, 0)
        except OSError:
            raise RuntimeError("Terminal process is not alive.")
        return True
    

    def get_command_history(self):
        with self.lock:
            return self.command_history

    def get_terminal_cwd(self):
        """Get current working directory of the opened terminal"""
        if not self._is_terminal_alive():
            print("Terminal is not running, returning current working directory.")
            return os.getcwd()  # Fallback if terminal not running
            
        # Write pwd command to terminal
        marker = f"__PWD_{int(time.time() * 1000)}__"
        self._write_to_terminal(f'pwd && echo "{marker}"')
        
        # Wait for output
        output_file = f"{self.script_path}.output"
        start_time = time.time()
        while time.time() - start_time < 5:  # 5 second timeout
            try:
                if os.path.exists(output_file):
                    with open(output_file, 'r') as f:
                        content = f.read()
                        if marker in content:
                            lines = content.splitlines()
                            for i, line in enumerate(lines):
                                if marker in line and i > 0:
                                    pwd_line = lines[i - 1].strip()
                                    return pwd_line

            except Exception as e:
                print(f"Error reading terminal output: {e}")
                pass
            time.sleep(0.1)
        
        return os.getcwd()  # Fallback on timeout

    def _send_to_llm(self, message):
        if self.llm:
            if message:
                message = message.strip()
                message += f"\n\nAll the commands run so far:{self.get_command_history()}\nCurrentDirectory we are in:{self.get_terminal_cwd()}\n"
                print("\n\nSending message to LLM via _send_to_llm:", message, end='\n\n')
                self.llm.debug_with_gpt(message)
            else:
                raise ValueError("Message cannot be empty.")
        else:
            raise ValueError("LLM is not set. Please set it using set_llm method.")

    def _log_to_history(self, entry):
        print("Logging to history:", entry)
        """Log command or message to history"""
        with self.lock:
            self.command_history.append(entry)

    def _is_terminal_alive(self):
        """Check if terminal process is still running"""
        # print("Checking if terminal is alive... from _is_terminal_alive")
        if self.process:
            return self.process.poll() is None
        return True

    def _write_to_terminal(self, command):
        """Write command to the terminal through the input file"""
        print("Writing to terminal:", command)
        if self.script_path:
            with open(f"{self.script_path}.input", 'w') as f:
                f.write(command)

    def send_input(self, user_input: str):
        """Send user input to the terminal"""
        print("Sending input to terminal:", user_input)
        self.input_queue.put(user_input)
        self._log_to_history({"queued_input": user_input})

    def _open_new_terminal(self):
        """Opens a new terminal window based on OS"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.script_path = os.path.join(tempfile.gettempdir(), f"agent_terminal_{timestamp}")
        
        # Get and validate the working directory
        
        print(f"Current working directory: {self.working_dir}")
        
        # # Create directory if it doesn't exist
        # if not os.path.exists(current_dir):
        #     os.makedirs(current_dir)
        #     print(f"Created directory: {current_dir}")
    
        if self.os_type == "darwin":  # macOS
            print(f"Detected macOS, using Terminal.app in directory: {self.working_dir}")
            self.script_path += ".command"
            self._create_terminal_script()
            
            # Create an AppleScript that opens Terminal in the correct directory
            apple_script = f'''
            tell application "Terminal"
                do script "cd '{self.working_dir}' && chmod +x '{self.script_path}' && '{self.script_path}'"
                activate
            end tell
            '''
            subprocess.Popen(["osascript", "-e", apple_script])
            
        elif self.os_type == "linux":
            self.script_path += ".sh"
            self._create_terminal_script()
            # Try different terminal emulators
            terminals = ["gnome-terminal", "xterm", "konsole"]
            for term in terminals:
                try:
                    self.process = subprocess.Popen([term, "--working-directory", self.working_dir, 
                                                  "--", "bash", self.script_path])
                    break
                except FileNotFoundError:
                    continue
            
        elif self.os_type == "windows":
            self.script_path += ".bat"
            self._create_terminal_script(for_windows=True)
            self.process = subprocess.Popen(
                ["start", "cmd", "/k", f"cd /d {self.working_dir} && {self.script_path}"],
                shell=True,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        
        self.child_pid = self.process.pid if self.process else 1
        self._start_monitor()

    def _create_terminal_script(self, for_windows=False):
        """Creates the terminal script with command handling logic"""
        print("Creating terminal script at:", self.script_path)
        output_file = f"{self.script_path}.output"
        
        if for_windows:
            script_content = f'''@echo off
:loop
set /p command=<"{self.script_path}.input"
if defined command (
    echo Executing: %command%
    %command% > "{output_file}" 2>&1
    echo __DONE_MARKER__ >> "{output_file}"
    echo. > "{self.script_path}.input"
)
timeout /t 1 /nobreak >nul
goto loop
'''
        else:
            script_content = f'''#!/bin/bash
# Enable error reporting and save command history
set -e
export HISTFILE="{self.script_path}.history"

# Initialize files and set initial working directory
touch "{self.script_path}.input"
touch "{self.script_path}.cwd"

# Ensure we start in the correct working directory
cd "{self.working_dir}"
echo "{self.working_dir}" > "{self.script_path}.cwd"

# Function to ensure we're in the correct directory
ensure_directory() {{
    current_dir="$(cat "{self.script_path}.cwd")"
    if [ "$PWD" != "$current_dir" ]; then
        cd "$current_dir"
    fi
}}

while true; do
    if [ -s "{self.script_path}.input" ]; then
        command=$(cat "{self.script_path}.input")
        if [ ! -z "$command" ]; then
            echo "Executing: $command"
            
            # Ensure correct directory before each command
            ensure_directory
            
            # Execute command and capture status
            {{ 
                eval "$command"
                cmd_status=$?
                echo $cmd_status > "{self.script_path}.status"
                if [ $cmd_status -eq 0 ]; then
                    echo "__SUCCESS__" >> "{output_file}"
                else
                    echo "__FAILED__" >> "{output_file}"
                fi
                # Save new working directory if changed
                pwd > "{self.script_path}.cwd"
                echo "__DONE_MARKER__" >> "{output_file}"
            }} 2>&1 | tee -a "{output_file}"
            
            # Cleanup
            echo "" > "{self.script_path}.input"
            sync
        fi
    fi
    sleep 0.5
done
'''
        
        with open(self.script_path, 'w') as f:
            f.write(script_content)
        
        if not for_windows:
            os.chmod(self.script_path, 0o755)
        
        # Create empty input file
        open(f"{self.script_path}.input", 'w').close()

    def _start_monitor(self):
        """Start monitoring the terminal output"""
        output_file = f"{self.script_path}.output"
        
        def monitor():
            last_size = 0
            while self._is_terminal_alive():
                try:
                    if os.path.exists(output_file):
                        current_size = os.path.getsize(output_file)
                        if current_size > last_size:
                            with open(output_file, 'r') as f:
                                content = f.read()
                                if content:
                                    self.output_buffer = content
                                    if "__DONE_MARKER__" in content:
                                        print("Command completion marker detected")
                                        self.command_completed.set()
                                        # Clear the output file
                                        open(output_file, 'w').close()
                        last_size = current_size
                    time.sleep(0.1)
                except Exception as e:
                    self._log_to_history({"monitor_error": str(e)})
                    continue

        self.monitor_thread = threading.Thread(target=monitor, daemon=True)
        self.monitor_thread.start()

    def run_commands(self, commands):
        print("Commands to run:", commands)
        if isinstance(commands, str):
            commands = [cmd.strip() for cmd in commands.split(",")]
        elif isinstance(commands, list):
            commands = [cmd.strip() for cmd in commands]
        else:
            self._send_to_llm("Commands must be a list or comma-separated string.")
            return

        if not self._is_terminal_alive():
            self._open_new_terminal()
            time.sleep(1)  # Give terminal time to initialize
        success_messages = []
        for cmd in commands:
            print(f"Running command: {cmd}")
            self.command_completed.clear()
            self.output_buffer = ""
            
            
            # Execute command and wait for completion
            self._write_to_terminal(f'echo ">>> Running: {cmd}"; {cmd}')
            
            if self.command_completed.wait(timeout=60):
                if "__FAILED__" in self.output_buffer:
                    self._log_to_history({cmd: "Failed"})
                    self._send_to_llm(f"Command failed: {cmd}\nOutput:\n{self.output_buffer}")
                else:
                    self._log_to_history({cmd: "Success"})
                    success_messages.append({cmd: self.output_buffer.strip()})
                    # If it's a cd command, verify the directory change
                    if cmd.startswith('cd '):
                        time.sleep(0.5)  # Give filesystem time to update
                        new_dir = self.get_terminal_cwd()
                        print(f"Changed directory to: {new_dir}")
                    print(f"\n\nCommands History: {self.get_command_history()}\n\n")
            else:
                self._log_to_history({cmd: "Timeout"})
                self._send_to_llm(f"Command timeout: {cmd}")
        self.llm.messages.append({"role": "assistant", "content": f"Commands executed: {success_messages}"})


    def write_to_file(self, filename, content):
        """Write content to a file with proper error handling"""
        try:
            # Convert relative path to absolute if needed
            if not os.path.isabs(filename):
                filename = os.path.join(self.working_dir, filename)
                
            # Create directory structure if it doesn't exist
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            # Write content to file
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
                
            print(f"Successfully wrote to: {filename}")
            self._log_to_history({"file_written": filename})
            return True
            
        except Exception as e:
            error_msg = f"Error writing to {filename}: {str(e)}"
            print(error_msg)
            self._log_to_history({"file_error": error_msg})
            return False