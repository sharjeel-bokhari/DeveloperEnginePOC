import subprocess
import platform
import os
import tempfile
import shlex
import datetime
import re

class TerminalManager:
    # before sending another llm request first run the update command history function
    def __init__(self):
        self.terminal_process = None
        self.command_history = []

    def run_llm_commands_in_new_terminal(self, commands):
        print("Entering Run LLM Commands in New Terminal")
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.last_log_file = os.path.join(tempfile.gettempdir(), f"terminal_log_{timestamp}.txt")

        script_content = "\n".join(commands) + "\n"
        self.command_history.extend(commands)

        system = platform.system()

        if system == "Windows":
            script_file = tempfile.NamedTemporaryFile(delete=False, suffix=".ps1", mode="w", encoding="utf-8")
            script_file.write(f"Start-Transcript -Path \"{self.last_log_file}\"\n")
            script_file.write(script_content)
            script_file.write("\nStop-Transcript\npause\n")
            script_file.close()

            subprocess.Popen(
                f'start powershell -NoExit -ExecutionPolicy Bypass -File "{script_file.name}"',
                shell=True
            )

        elif system == "Darwin":
            script_file = tempfile.NamedTemporaryFile(delete=False, suffix=".sh", mode="w", encoding="utf-8")
            escaped_log_path = shlex.quote(self.last_log_file)
            wrapped_commands = "\n".join(commands)
            script_file.write(f'script -q {escaped_log_path} bash <<EOF\n{wrapped_commands}\nexec bash\nEOF\n')
            script_file.close()
            os.chmod(script_file.name, 0o755)

            subprocess.Popen([
                "osascript", "-e",
                f'tell application \"Terminal\" to do script \"bash {script_file.name}\"'
            ])

        elif system == "Linux":
            script_file = tempfile.NamedTemporaryFile(delete=False, suffix=".sh", mode="w", encoding="utf-8")
            escaped_log_path = shlex.quote(self.last_log_file)
            wrapped_commands = "\n".join(commands)
            script_file.write(f'script -q {escaped_log_path} bash <<EOF\n{wrapped_commands}\nexec bash\nEOF\n')
            script_file.close()
            os.chmod(script_file.name, 0o755)

            subprocess.Popen(["gnome-terminal", "--", "bash", "-c", f"bash {script_file.name}"])

        else:
            raise OSError(f"Unsupported OS: {system}")

        print("Commands sent to terminal.")
        print("Log file:", self.last_log_file)
        print("Commands:")
        for cmd in commands:
            print("   ", cmd)
        print("-" * 40)

    def get_command_history(self):
        return self.command_history

    def update_command_history_from_log(self, log_file_path=None):
        """
        Parses the log file and appends user-entered commands to self.command_history.
        Should be called AFTER the user finishes their session.
        """
        log_file = log_file_path or getattr(self, "last_log_file", None)
        if not log_file or not os.path.exists(log_file):
            print("No valid log file to parse.")
            return

        with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

        new_commands = []

        system = platform.system()

        if system in ["Linux", "Darwin"]:
            for line in lines:
                line = line.strip()
                if line.startswith("$"):
                    cmd = line[1:].strip()
                    if cmd and cmd not in self.command_history:
                        new_commands.append(cmd)

        elif system == "Windows":
            capture = False
            for line in lines:
                line = line.strip()
                if line.startswith("PS ") or re.match(r"^.*> ", line):
                    parts = line.split(">", 1)
                    if len(parts) == 2:
                        cmd = parts[1].strip()
                        if cmd and cmd not in self.command_history:
                            new_commands.append(cmd)

        self.command_history.extend(new_commands)
        print(f"Appended {len(new_commands)} new commands from terminal session.")