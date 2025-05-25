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
        self.model = "gpt-4"
        self.terminal_manager = None
        # This is the response we get from the promptAction output
        self.responsePromptAction = ""
        self.userPrompt = ""
        self.dirStructure = ""
        # We will use this prompt to determine the user's intended action based on their request and the given project directory structure.
        # The prompt will be used to generate the JSON output based on the user's request and the directory structure.
        self.promptAction = f"""
            Your task is to determine the user's intended action based on their request and the given project directory structure.

            Actions and corresponding expected JSON outputs:
            - If the user wants to **analyze the directory structure**, return: {{"Action": "Analyze"}}
            - If the user wants to **add a new feature**, return: {{"Action": "Add", "File": "Full File Path"}}
            - If the user wants to **fix a bug**, evaluate the directory structure and return: {{"Action": "Fix", "File": "Full File Path"}}
            - If the user wants to **delete a file**, return: {{"Action": "Delete", "File": "Full File Path"}}
            - If the user wants to **create a new file**, return: {{"Action": "Create", "File": "Full File Path"}}
            - If the user wants to **edit a file**, return: {{"Action": "Edit", "File": "Full File Path"}}
            - If the user wants to **get the diff of a file**, return: {{"Action": "Diff", "File": "Full File Path"}}
            - If the user wants to **get the content of a file**, return: {{"Action": "Get", "File": "Full File Path"}}
            - If the user wants to **get the directory structure**, return: {{"Action": "Dir"}}
            - If the user wants to **get the tech stack**, return: {{"Action": "Tech"}}
            - If the user wants to **get the last checked files**, return: {{"Action": "LastCheckedFiles"}}
            - If the user wants to **get excluded directories** for a specific tech stack, return: {{"Action": "ExcludedDirs", "Tech": "Tech Stack"}}
            - If the user is working in the frontend and wants to create a backend, return: {{"Action": "LeaveFEAndCreateBE"}}
            - If the user is working in the backend and wants to create a frontend, return: {{"Action": "LeaveBEAndCreateFE"}}
            - If, judging by the users directory structure, the user has no project initialized, return: {{"Action: "InitalizeProject"}}
            - if the user needs to run any commands, return: {{"Action": "RunCommand", "Commands": "[Command1, Command2 ...]"}}. The commands should be in a list format.

            Directory structure: {self.dirStructure}

            **Rules:**
            1. Follow the format of the example outputs exactly—return **only** a single valid JSON object.
            2. Always refer to the **latest directory structure** provided.
            3. Ensure all suggestions **comply with the project's tech stack** and use the **latest version** of the tools or frameworks.
            4. For actions like **Fix**, **Edit**, **Get**, **Delete**, or **Diff**, only refer to files that **exist** in the directory structure.
            5. For the **Create** action, only refer to files that **do not exist**. If directories must be created, include them in the file path.

            **Example Outputs:**
            {{
                "Action": "Analyze"
            }}
            {{
                "Action": "Add",
                "File": "frontend/src/app/components/NewComponent.js"
            }}
            """
        # This prompt will be to generate a json output which will contain the code the user has requested.
        self.promptCode = f"""
            You are a Senior Software Engineer who excels in all modern tech stacks and understands user intent precisely.

            Your task is to perform the following action based on the user's request and return the appropriate result:

            Action: {self.responsePromptAction}
            Description: {self.userPrompt}

            **Rules:**
            1. Return only a **single valid JSON object** in your response.
            2. Always refer to the **latest project directory structure**.
            3. Ensure your solution complies with the **project's tech stack** and uses the **latest stable versions** of tools/frameworks.
            4. Your code should be **well-structured**, **clean**, and **easy to read**.
            5. When relevant, include necessary **import statements** and use **proper naming conventions**.
            6. If the action is "Fix", explain **what was wrong** and **how you fixed it** in a comment.
            7. If the action is "Edit" or "Add", return the **full updated content** of the file.
            8. If the action is "Diff", return only the code **diff** in standard diff format (using `+` and `-` lines).

            **Example Output:**
            {{
            "Action": "Add",
            "File": "frontend/src/components/LoginForm.tsx",
            "Content": "import React from 'react';\\n\\nconst LoginForm = () => {{\\n  return (\\n    <form className='login-form'>\\n      <input type='email' placeholder='Email' />\\n      <input type='password' placeholder='Password' />\\n      <button type='submit'>Login</button>\\n    </form>\\n  );\\n}};\\n\\nexport default LoginForm;"
            }}
        """

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
        self.debugMessages.append({"role": "user", "content": user_prompt})
        self.userPrompt = user_prompt
        print(f"Debugging with GPT: {user_prompt}")
        # Ask gpt to generate a response based on the debug messages
        debugResponse = self.ask_gpt(self.debugMessages)
        self.debugMessages = self.trim_history(self.debugMessages)
        try:
            decodedResponse = json.loads(debugResponse)
            self.debugMessages.append({"role": "assistant", "content": json.dumps(decodedResponse)})
            ans = self.takeAction(decodedResponse)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            # If the output is not a valid JSON, send it back to gpt for sending a better response
            self.debug_with_gpt(f"Error: {e} - {debugResponse}")
        return ans
    

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
Your task is to determine the user's intended action based on their request and the given project directory structure.

Actions and corresponding expected JSON outputs:
- If the user wants to **analyze the directory structure**, return: {{"Action": "Analyze", Commands: ["ls", "tree -I 'node_modules|.git|.env|.next|dist|build|target|bin|obj'"]}}
- If the user wants to **add a new feature**, return: {{"Action": "Add", "File": "Full File Path"}}
- If the user wants to **fix a bug**, evaluate the directory structure and return: {{"Action": "Fix", "File": "Full File Path"}}
- If the user wants to **delete a file**, return: {{"Action": "Delete", "File": "Full File Path"}}
- If the user wants to **create a new file**, return: {{"Action": "Create", "File": "Full File Path"}}
- If the user wants to **edit a file**, return: {{"Action": "Edit", "File": "Full File Path"}}
- If the user wants to **get the diff of a file**, return: {{"Action": "Diff", "File": "Full File Path"}}
- If the user wants to **get the content of a file**, return: {{"Action": "Get", "File": "Full File Path"}}
- If the user wants to **get the directory structure**, return: {{"Action": "Dir", Commands: [list directory commands, e.g., "cd folderName or tree -I 'node_modules|.git|.env|.next|dist|build|target|bin|obj'"]}}
- If the user wants to **get the tech stack**, return: {{"Action": "Tech"}}
- If the user wants to **get the last checked files**, return: {{"Action": "LastCheckedFiles"}}
- If the user wants to **get excluded directories** for a specific tech stack, return: [{{"Action": "ExcludedDirs", "Tech": "Tech Stack"}}]
- If the user is working in the frontend and wants to create a backend, return: [{{"Action": "LeaveFEAndCreateBE", "Commands": [Command1, Command2 ...]}}]
- If the user is working in the backend and wants to create a frontend, return: {{"Action": "LeaveBEAndCreateFE", "Commands": [Command1, Command2 ...]}}
- If, judging by the users directory structure, the user has no project initialized, return: {{"Action: "InitalizeProject"}}
- if the user needs to run any commands, return: {{"Action": "RunCommand", "Commands": [Command1, Command2 ...]}}. The commands should be in a list format.

Directory structure:
\n{self.getDirStructure()[0]}\n

**Rules:**
1. Follow the format of the example outputs exactly—return **only** a single valid JSON object.
2. Always refer to the **latest directory structure** provided.
3. Ensure all suggestions **comply with the project's tech stack** and use the **latest version** of the tools or frameworks.
4. For actions like **Fix**, **Edit**, **Get**, **Delete**, or **Diff**, only refer to files that **exist** in the directory structure.
5. For the **Create** action, only refer to files that **do not exist**. If directories must be created, include them in the file path.
6. If the parent directory is this "/Users/sharjeelbokhari/Documents/BODEVS/DeveloperEngineHome 2", then you are to assume that you are in the root user.
7. Never add any code tags to the output, like ```json or ```python or ```jsx and so on. Just return the JSON object as it is.
8. Use the Names of the Directories and Files as they are, do not change them to lower case or upper case. Use the exact same names as they are in the directory structure.


**Example Outputs:**
{{
    "Action": "Analyze"
}}
{{
    "Action": "Add",
    "File": "frontend/src/app/components/NewComponent.js"
}}
"""
    def generate_prompt_code(self, action_data, user_prompt):
        action = action_data["Action"]
        file = action_data.get("File")
        file_content = None

        if action in ["Edit", "Fix", "Diff", "Get"] and file:
            file_path = os.path.join(*file.split("/"))
            file_content = self.getFileContent(file_path)


        base_prompt = f"""
You are a Senior Software Engineer who excels in all modern tech stacks and understands user intent precisely.

Your task is to perform the following action based on the user's request and return the appropriate result:

Action: {action_data}
Description: {user_prompt}
"""
        if file_content and action in ["Edit", "Fix", "Diff", "Get"]:
            base_prompt += f"\nCurrent file content:\n{file_content}\n"

        base_prompt += """
**Rules:**
1. Return only a **single valid JSON object** in your response.
2. Always refer to the **latest project directory structure**.
3. Ensure your solution complies with the **project's tech stack** and uses the **latest stable versions** of tools/frameworks.
4. Your code should be **well-structured**, **clean**, and **easy to read**.
5. When relevant, include necessary **import statements** and use **proper naming conventions**.
6. If the action is "Fix", explain **what was wrong** and **how you fixed it** in a comment.
7. If the action is "Edit" or "Add", return the **full updated content** of the file.
8. If the action is "Diff", return only the code **diff** in standard diff format (using `+` and `-` lines).
9. Use the Names of the Directories and Files as they are, do not change them to lower case or upper case. Use the exact same names as they are in the directory structure.

**Example Output:**
{{
"Action": "Add",
"File": "frontend/src/components/LoginForm.tsx",
"Content": "import React from 'react';\\n\\nconst LoginForm = () => {{\\n  return (\\n    <form className='login-form'>\\n      <input type='email' placeholder='Email' />\\n      <input type='password' placeholder='Password' />\\n      <button type='submit'>Login</button>\\n    </form>\\n  );\\n}};\\n\\nexport default LoginForm;"
}}
"""
        return base_prompt

    def generate_response(self, prompt):
        self.userPrompt = prompt
        self.promptAction = self.generate_prompt_action()
        print(f"\n\nGenerating response for prompt: {self.promptAction}\n\n")
        self.messages.append({"role": "system", "content": self.promptAction})
        self.messages.append({"role": "user", "content": prompt})
        self.responsePromptAction = self.ask_gpt(self.messages)
        print(f"Response from GPT: {self.responsePromptAction}")
        self.messages.append({"role": "assistant", "content": self.responsePromptAction})
        self.messages = self.trim_history(self.messages)

        # Generate the code based on the action
        try:
            print("Decoding responsePromptAction to JSON...")
            output = json.loads(self.responsePromptAction)
        except json.JSONDecodeError as e:
            # If the output is not a valid JSON, return the error message
            return f"# Error promptAction: {e} - {self.responsePromptAction}"
        # Judging by the action to be performed, we will either generate the code or run the commands.
        ans = self.takeAction(output)
            # Return the output
        return ans

    def takeAction(self, output):
        outputAction = output["Action"]
        print(f"Action to be performed: {outputAction}")
        if outputAction in ["RunCommand", "Run", "LeaveBEAndCreateFE", "LeaveFEAndCreateBE"]:
            commands = output["Commands"]
            # Run the commands in an orderly manner
            if self.terminal_manager is None:
                raise ValueError("Terminal manager is not set. Please set it using set_terminal_manager method.")
            self.terminal_manager.run_commands(commands)
            return f"Commands executed: {commands}"
        elif outputAction == "Dir":
            # Get the directory structure
            if self.terminal_manager is None:
                raise ValueError("Terminal manager is not set. Please set it using set_terminal_manager method.")
            commands_to_run = output["Commands"]
            print(f"\n\nCommands to run for directory structure: {commands_to_run}")
            self.terminal_manager.run_commands(commands_to_run)
            # Add the directory structure to the output
            # Return the output
            return output
        elif outputAction == "Tech":
            # Get the tech stack
            if self.terminal_manager is None:
                raise ValueError("Terminal manager is not set. Please set it using set_terminal_manager method.")
            # Get the tech stack from the current working directory
            tech_stack = self.detect_tech_stack(self.terminal_manager.get_terminal_cwd())
            # Add the tech stack to the output
            output["Tech"] = tech_stack
            # Return the output
            return output
        elif outputAction == "Analyze":
            commands_to_run = output["Commands"]
            print("\n\nCommands to run for analysis:", commands_to_run)
            if self.terminal_manager is None:
                raise ValueError("Terminal manager is not set. Please set it using set_terminal_manager method.")
            # Run the commands in an orderly manner
            self.terminal_manager.run_commands(commands_to_run)

            return output

        else:
            # Generate the code based on the action
            prompt_code = self.generate_prompt_code(output, self.userPrompt)
            # Get the code from gpt
            self.messages.append({"role": "system", "content": prompt_code})
            code = self.ask_gpt(self.messages, temperature=0.5)
            print(f"Code generated: {code}")
            self.messages.append({"role": "assistant", "content": code})
            self.messages = self.trim_history(self.messages)
            # Write the code to the file
            try:
                code = json.loads(code)
            except json.JSONDecodeError as e:
                # If the output is not a valid JSON, return the error message
                return f"# Error code: {e} - {code}"
            codeAction = code["Action"]
            filePath = code["File"]
            contentToWrite = code["Content"]
            print(f"Code Action: {codeAction}, File Path: {filePath}, Content Length: {len(contentToWrite)}")
            if codeAction == "Add":
                # Check if the file path exists
                # If the whole path exists, we will create the file in the path
                # If the whole path does not exist, we will go upto the last directory that exists and create the new directory
                # and then create the file in that directory
                print(f"Adding file at path: {filePath}")
                try:
                    if os.path.exists(filePath):
                        # If the file already exists, we will overwrite it
                        with open(filePath, "w") as file:
                            file.write(contentToWrite)
                    else:
                        dir_path = os.path.dirname(filePath)

                        # Traverse up until we find an existing directory
                        existing_path = dir_path
                        while not os.path.exists(existing_path) and existing_path != os.path.dirname(existing_path):
                            existing_path = os.path.dirname(existing_path)

                        # If no existing parent was found, raise an error
                        if not os.path.exists(existing_path):
                            raise FileNotFoundError("No part of the path exists. Cannot proceed safely.")

                        # Get the relative subpath to create
                        to_create = os.path.relpath(dir_path, existing_path)
                        full_create_path = os.path.join(existing_path, to_create)

                        # Create only the missing subdirectories
                        if not os.path.exists(full_create_path):
                            os.makedirs(full_create_path)

                        # Finally, write the file
                        with open(filePath, 'w') as f:
                            f.write(contentToWrite)
                        f.close()
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    print(exc_type, fname, exc_tb.tb_lineno)
            elif codeAction == "Edit":
                # Check if the file path exists
                if os.path.exists(filePath):
                    # If the file already exists, we will overwrite it
                    with open(filePath, "w") as file:
                        file.write(contentToWrite)
                else:
                    if self.terminal_manager is not None:
                        # If the file does not exist, we will create the file in the path
                        self.terminal_manager._send_to_llm(f"File '{filePath}' does not exist. Cannot edit.")
                    else:
                        # If the file does not exist, we will create the file in the path
                        raise ValueError("self.terminal_manager is None. Cannot edit the file.")
            elif codeAction == "Delete":
                # Check if the file path exists
                if os.path.exists(filePath):
                    # If the file already exists, we will delete it
                    os.remove(filePath)
                else:
                    if self.terminal_manager is not None:
                        # If the file does not exist, we will create the file in the path
                        self.terminal_manager._send_to_llm(f"File '{filePath}' does not exist. Cannot delete.")
                    else:
                        # If the file does not exist, we will create the file in the path
                        raise ValueError("self.terminal_manager is None. Cannot delete the file.")
            elif codeAction == "Diff":
                # Check if the file path exists
                if os.path.exists(filePath):
                    # If the file already exists, we will get the diff of the file
                    with open(filePath, "r") as file:
                        fileContent = file.read()
                        diff = self.get_diff(fileContent, contentToWrite)
                        output["Diff"] = diff
                else:
                    if self.terminal_manager is not None:
                        # If the file does not exist, we will create the file in the path
                        self.terminal_manager._send_to_llm(f"File '{filePath}' does not exist. Cannot get diff.")
                    else:
                        # If the file does not exist, we will create the file in the path
                        raise ValueError("self.terminal_manager is None. Cannot get diff.")
            elif codeAction == "Get":
                # Check if the file path exists
                if os.path.exists(filePath):
                    # If the file already exists, we will get the content of the file
                    return self.getFileContent(filePath)
                else:
                    if self.terminal_manager is not None:
                        # If the file does not exist, we will create the file in the path
                        self.terminal_manager._send_to_llm(f"File '{filePath}' does not exist. Cannot get content.")
                    else:
                        # If the file does not exist, we will create the file in the path
                        raise ValueError("self.terminal_manager is None. Cannot get content.")
            elif codeAction == "LastCheckedFiles":
                # Check if the last checked files exist
                if self.lastCheckedFiles:
                    # If the last checked files exist, we will get the content of the file
                    return self.lastCheckedFiles
                else:
                    raise ValueError("self.terminal_manager is None. No last checked files found.")
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

    def getDirStructure(self, root_path=None):
        # This function gets the file structure ignoring files like node_modules, .env, .next, etc.
        if root_path is None:
            if self.terminal_manager is None:
                raise ValueError("Terminal manager is not set. Please set it using set_terminal_manager method.")
            root_path = self.terminal_manager.get_terminal_cwd()
        print(f"\n\nUsing terminal's current working directory: {root_path}", end='\n\n')

        tech = self.detect_tech_stack(root_path)
        excluded_dirs = self.get_excluded_dirs_for_tech(tech)

        print(f"Detected Tech Stack: {tech}")
        print(f"Excluding directories: {excluded_dirs}\n")

        structure = []

        for dirpath, dirnames, filenames in os.walk(root_path):
            # Filter directories to skip excluded ones
            dirnames[:] = [d for d in dirnames if d not in excluded_dirs]

            structure.append({
                "path": dirpath,
                "dirs": dirnames[:],
                "files": filenames
            })

        return structure

    def get_excluded_dirs_for_tech(self, tech):
        # Define folders to ignore for each tech stack
        tech_excludes = {
            'nextjs': {'.next', 'node_modules', '.env', '.turbo', '.git'},
            'node': {'node_modules', 'dist', '.env', '.git'},
            'react': {'node_modules', 'build', '.env', '.git'},
            'angular': {'node_modules', 'dist', '.angular', '.env', '.git'},
            'vue': {'node_modules', 'dist', '.env', '.git'},
            'python': {'__pycache__', '.env', '.venv', 'venv', '.git'},
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