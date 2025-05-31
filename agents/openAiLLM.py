import platform
from openai import OpenAI
import os
import sys
import json
import subprocess
from dotenv import load_dotenv

load_dotenv()


class OpenAIClient:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4.1-2025-04-14"
        self.terminal_manager = None
        # This is the response we get from the promptAction output
        self.responsePromptAction = ""
        self.userPrompt = ""
        self.dirStructure = ""
        # We will use this prompt to determine the user's intended action based on their request and the given project directory structure.
        # The prompt will be used to generate the JSON output based on the user's request and the directory structure.
        self.promptAction = ""
        # This prompt will be to generate a json output which will contain the code the user has requested.
        self.promptCode = ""
        self.messages = []
        self.debugMessages = [{"role": "system", "content": self.promptAction}]

        self.lastCheckedFiles = []

    def set_terminal_manager(self, terminal_manager):
        # This function is used to set the terminal manager for the client.
        self.terminal_manager = terminal_manager
        
    def process_user_prompt(self, user_prompt):
        """
        Processes the user's prompt, determines the intended action, and executes it.
        Returns the result or output of the action.
        """
        self.userPrompt = user_prompt
        try:
            # Generate and process the response for the user's prompt
            result = self.generate_response(user_prompt)
            return result
        except Exception as e:
            return f"[Agent Error]: {str(e)}"
    def debug_with_gpt(self, user_prompt):
        # This function is used to debug the code with gpt.
        # It will take the user prompt and return the response from gpt.
        # self.debugMessages.append({"role": "user", "content": user_prompt})
        self.messages.append({"role": "user", "content": user_prompt})
        self.userPrompt = user_prompt
        print(f"Debugging with GPT: {user_prompt}")
        # Ask gpt to generate a response based on the debug messages
        debugResponse = self.generate_response(self.userPrompt)
        print(f"Debug response from GPT: {debugResponse}")
        # self.messages = self.trim_history(self.messages)
        # try:
        #     decodedResponse = json.loads(debugResponse)
        #     self.debugMessages.append({"role": "assistant", "content": json.dumps(decodedResponse)})
        #     ans = self.takeAction(decodedResponse)
        # except json.JSONDecodeError as e:
        #     print(f"Error decoding JSON: {e}")
        #     # If the output is not a valid JSON, send it back to gpt for sending a better response
        #     self.debug_with_gpt(f"Error: {e} - {debugResponse}")
        # return ans
    

    def ask_gpt(self, messages, temperature = 0):
        # This function is used to give gpt the right context and prompt and ask it to generate a response.
        print(f"Entering ask_gpt with temperature: {temperature}")
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature
        )
        llmResponse = response.choices[0].message.content
        return llmResponse
    def generate_prompt_action(self):
        return f"""
You are a Senior Software Engineer who excels in understanding user intent precisely and performing complex operations across modern tech stacks.

Your task is to analyze the user's request and determine **what actions need to be performed**.

---

### Output Format:
Return a single valid JSON object containing:

- `"Action"` (string) for a single action (e.g., "Edit", "Add", "Analyze")
  **OR**
- `"Actions"` (list of strings) if the request involves multiple steps (e.g., ["Analyze", "Edit", "Refactor"])

- `"Description"` (string): A concise explanation of what the action(s) will do — ideally mentioning specific files or goals if available.

---
### Context:
Directory Structure: {self.getDirStructure()}
### Example 1: Single Action

{{
  "Action": "Analyze",
  "Description": "Analyze the codebase to understand the project structure and suggest improvements."
}}

### Example 2: Multiple Actions & File Mentions
{{
  "Actions": ["Analyze", "Edit", "Add"],
  "Description": "Analyze the directory structure, edit 'frontend/src/pages/Home.tsx' to add a button, and create a new file 'frontend/src/components/Button.tsx' for the reusable button component."
}}
### Rules:
Be specific but concise.
Describe the actions at a high level, not line-by-line implementation.
Include filenames or folder paths in the description if the user's request mentions them.
Only return the JSON — no explanation or commentary.
"""
    def generate_prompt_code(self, action_data):
        action = None
        try:
            action = action_data["Action"]
        except KeyError:
            try:
                action = action_data["Actions"]
            except KeyError:
                raise ValueError("Action or Actions not found in the action_data. Please provide a valid action.")
        if action is None:
            raise ValueError("Action is None. Please provide a valid action.")
        description = action_data.get("Description", "No description provided.")

        return f"""
You are a Senior Software Engineer who generates and modifies code precisely based on the user's intent and directory structure.

Your task is to:
- Write all necessary terminal commands (e.g., create files, install packages, navigate folders),
- Provide source code changes, which may involve **one or more files**.

### Output Format:
Return a single **valid JSON object** with:
- `"Action"`: (string) The action being executed.
- `"Commands"`: (list of strings) Shell commands that should be executed.
- `"Codes"`: Either
  - A **single object** with `"File"` and `"Content"` fields (for one file),
  - **OR** a **list of objects**, each with:
    - `"File"`: (string) — The file path.
    - `"Content"`: (string) — Full source code or updated content.

---
### Context:
Action: {action}
Descrition: {description}
---
### Example: Single File

{{
  "Action": "Edit",
  "Commands": ["code frontend/src/components/Button.tsx"],
  "Codes": {{
    "File": "frontend/src/components/Button.tsx",
    "Content": "export const Button = () => <button>Click Me</button>;"
  }}
}}

### Example: Multiple Files

{{
  "Action": "Add",
  "Commands": [
    "mkdir -p frontend/src/components/common",
    "touch frontend/src/components/common/Header.tsx",
    "touch frontend/src/components/common/Footer.tsx"
  ],
  "Codes": [
    {{
      "File": "frontend/src/components/common/Header.tsx",
      "Content": "export const Header = () => <header>Header</header>;"
    }},
    {{
      "File": "frontend/src/components/common/Footer.tsx",
      "Content": "export const Footer = () => <footer>Footer</footer>;"
    }}
  ]
}}
### Rules:
All file contents must be properly escaped.
Your JSON must be valid and minifiable.
Preserve indentation and code quality.
Only return the JSON. Do not explain or annotate it.
For editing existing files, include the full content of the file, not just the changes.
Make sure to include all necessary commands to create or modify files.
Make sure to keep the codes clean, modular, re-usable and well-structured.
"""

    def generate_response(self, prompt):
        self.userPrompt = prompt
        # Generate the promptAction based on the user's request
        self.promptAction = self.generate_prompt_action()
        print(f"\n\nGenerating response for prompt\n\n")

        self.messages.append({"role": "system", "content": self.promptAction})
        self.messages.append({"role": "user", "content": prompt})

        self.responsePromptAction = self.ask_gpt(self.messages)

        print(f"Response from GPT Analyzer: {self.responsePromptAction}")
        self.messages.append({"role": "assistant", "content": self.responsePromptAction})
        
        # This is where we send the response we get from the analyser prompt to the coding prompt.
        try:
            action_data = json.loads(self.responsePromptAction)
            self.promptCode = self.generate_prompt_code(action_data)
            print(f"\n\nGenerating prompt for code generation:\n\n")
            self.messages.append({"role": "system", "content": self.promptCode})

            # Ask gpt to generate the code based on the promptCode
            codeResponse = self.ask_gpt(self.messages, temperature=0.5)
            print(f"\n\nCode response from GPT: {codeResponse}\n")
            self.messages.append({"role": "assistant", "content": codeResponse})
            
            self.takeAction(codeResponse)
            
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            # If the output is not a valid JSON, send it back to gpt for sending a better response
            self.debug_with_gpt(f"Error: {e} - {self.responsePromptAction}")
            return f"[Agent Error]: {e}"

    def takeAction(self, output):
        """Handle different actions based on GPT response"""
        try:
            if isinstance(output, str):
                output_data = json.loads(output)
            else:
                output_data = output
                
            action = output_data.get("Action")
            commands = output_data.get("Commands", [])
            codes = output_data.get("Codes", [])
            
            print(f"\nAction: {action}, Commands: {commands}, Codes: {codes}\n")

            if not isinstance(codes, list):
                codes = [codes] if codes else []

            # Execute commands first
            if commands:
                if self.terminal_manager is None:
                    raise ValueError("Terminal manager is not set")
                print(f"Executing commands: {commands}")
                self.terminal_manager.run_commands(commands)

            # Then handle file operations
            if codes:
                for code_item in codes:
                    if isinstance(code_item, dict):
                        file_path = code_item.get("File")
                        content = code_item.get("Content")
                        
                        if file_path and content:
                            print(f"Writing to file: {file_path}")
                            # Ensure absolute path
                            if not os.path.isabs(file_path):
                                file_path = os.path.join(self.terminal_manager.working_dir, file_path)
                            
                            # Create directory if it doesn't exist
                            os.makedirs(os.path.dirname(file_path), exist_ok=True)
                            
                            # Write content to file
                            try:
                                with open(file_path, 'w', encoding='utf-8') as f:
                                    f.write(content)
                                print(f"Successfully wrote to {file_path}")
                            except Exception as e:
                                print(f"Error writing to {file_path}: {e}")
                                return f"[Agent Error]: Failed to write to {file_path}: {e}"

            return "Actions completed successfully"

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return f"[Agent Error]: {e}"
        except Exception as e:
            print(f"Error taking action: {e}")
            return f"[Agent Error]: {e}"


    def trim_history(self, messages):
        # Always keep the latest system message (usually first message)
        system_msgs = [msg for msg in messages if msg["role"] == "system"]
        latest_system = system_msgs[-1] if system_msgs else None

        # Filter out system messages
        non_system_msgs = [msg for msg in messages if msg["role"] != "system"]

        # Keep only the last 4 non-system messages
        trimmed_non_system = non_system_msgs[-4:]

        # Rebuild history: one system message + last 4 user/assistant messages
        messages = [latest_system] + trimmed_non_system if latest_system else trimmed_non_system
        return messages

    def getFileContent(self, file_path):
        # Track the file for future reference
        self.lastCheckedFiles.append(file_path)

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            return f"# Error: File '{file_path}' not found."
        except Exception as e:
            return f"# Error reading file '{file_path}': {e}"

    def getDirStructure(self, root_path=None, indent='    '):
        """
        Returns the file structure of a directory, excluding certain folders based on the tech stack.
        """
        if root_path is None:
            if self.terminal_manager is None:
                raise ValueError("Terminal manager is not set. Please set it using set_terminal_manager method.")
            root_path = self.terminal_manager.working_dir
        root_path = os.path.abspath(root_path)
        
        print(f"\n\nUsing terminal's current working directory: {root_path}\n")

        tech = self.detect_tech_stack(root_path)
        excluded_dirs = self.get_excluded_dirs_for_tech(tech)

        print(f"Detected Tech Stack: {tech}")
        print(f"Excluding directories: {excluded_dirs}\n")

        structure = []
        #  Running a Tree command to get the directory structure
        if platform.system() == "Windows":
            # Use 'tree' command for Windows
            tree_command = f'tree "{root_path}" /F /A'
        else:
            # Use 'tree' command for Unix-like systems
            tree_command = f'tree "{root_path}" -I "{"|".join(excluded_dirs)}" -a'

        try:
            print(f"Running command: {tree_command}")
            result = subprocess.run(tree_command, shell=True, capture_output=True, text=True, check=True)
            print(f"Command output:\n{result.stdout}")
            structure.append(result.stdout)
            return structure
        except subprocess.CalledProcessError as e:
            print(f"Error running tree command: {e}")
            return f"[Agent Error]: {e}"
        
            
        # for root, dirs, files in os.walk(root_path):
        #     # Filter out excluded directories
        #     dirs[:] = [d for d in dirs if d not in excluded_dirs]

        #     # Compute depth
        #     level = root.replace(root_path, '').count(os.sep)
        #     indent_str = indent * level
        #     dir_line = f"{indent_str}├── {os.path.basename(root)}/"
        #     print(dir_line)
        #     structure.append(dir_line)

        #     subindent = indent * (level + 1)
        #     for f in files:
        #         file_line = f"{subindent}└── {f}"
        #         print(file_line)
        #         structure.append(file_line)

        # return structure


    def get_excluded_dirs_for_tech(self, tech):
        # Define folders to ignore for each tech stack
        tech_excludes = {
            'nextjs': {'.next', 'node_modules', '.env', '.turbo', '.git'},
            'node': {'node_modules', 'dist', '.env', '.git'},
            'react': {'node_modules', 'build', '.env', '.git'},
            'angular': {'node_modules', 'dist', '.angular', '.env', '.git'},
            'vue': {'node_modules', 'dist', '.env', '.git'},
            'python': {'__pycache__', '.env', '.venv', 'venv', '.git', 'node_modules'},
            'django': {'__pycache__', 'migrations', '.env', '.git'},
            'flask': {'__pycache__', '.env', '.git'},
            'fastapi': {'__pycache__', '.env', '.git'},
            'java': {'target', '.git'},
            'spring': {'target', '.git'},
            'dotnet': {'bin', 'obj', '.git'},
            'rust': {'target', '.git'},
            'go': {'bin', '.git'},
            'php': {'vendor', '.env', '.git'},
            'laravel': {'vendor', 'storage', '.env', '.git'},
            'ruby': {'.bundle', 'log', 'tmp', '.git'},
            'rails': {'log', 'tmp', 'node_modules', '.git'},
            'android': {'build', '.gradle', '.idea', '.git'},
            'generic': {'.git', '.idea', '.vscode', '.env', '__pycache__'},
            'root': {'agents', 'managers', 'main.py', 'Logic.txt', '.env'}
        }

        return tech_excludes.get(tech, tech_excludes['generic'])

    def detect_tech_stack(self, project_path='.'):
        
        files = set(os.listdir(project_path))

        tech_signatures = {
            'nextjs': {'next.config.js', '.next'},
            'node': {'package.json', 'node_modules'},
            'react': {'package.json', 'public', 'src'},
            'angular': {'angular.json', 'tsconfig.json'},
            'vue': {'vite.config.js', 'vue.config.js'},
            'python': {'main.py', 'requirements.txt', 'pyproject.toml', '__pycache__'},
            'django': {'manage.py', 'settings.py'},
            'flask': {'app.py', 'run.py'},
            'fastapi': {'main.py', 'app', 'routers'},
            'java': {'pom.xml', 'build.gradle'},
            'spring': {'application.properties', 'application.yml', 'pom.xml'},
            'dotnet': {'*.csproj'},
            'rust': {'Cargo.toml'},
            'go': {'go.mod', 'main.go'},
            'php': {'composer.json', 'index.php'},
            'laravel': {'artisan', '.env', 'routes', 'app'},
            'ruby': {'Gemfile', 'config.ru'},
            'rails': {'Gemfile', 'config.ru', 'bin', 'db'},
            'android': {'build.gradle', 'AndroidManifest.xml'},
        }

        for tech, indicators in tech_signatures.items():
            for indicator in indicators:
                # Support wildcard matching
                if '*' in indicator:
                    from fnmatch import fnmatch
                    if any(fnmatch(f, indicator) for f in files):
                        return tech
                elif indicator in files or os.path.exists(os.path.join(project_path, indicator)):
                    return tech

        return 'generic'