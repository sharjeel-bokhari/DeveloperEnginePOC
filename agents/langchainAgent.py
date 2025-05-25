import os
import difflib
import hashlib
import json
import re
from openai import OpenAI
from dotenv import load_dotenv
from langchain.agents import initialize_agent, Tool
from langchain.agents.agent_types import AgentType
from langchain.chat_models import ChatOpenAI
from langchain.tools import tool

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
llm = ChatOpenAI(model_name="gpt-4o", temperature=0)


# ========== Utility Functions ==========

def hash_file(filepath):
    with open(filepath, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()

def get_all_files(base_dir="."):
    ignored_dirs = {'.git', 'node_modules', '.env', '__pycache__', 'dist', 'build'}
    all_files = []
    for root, dirs, files in os.walk(base_dir):
        dirs[:] = [d for d in dirs if d not in ignored_dirs]
        for file in files:
            full_path = os.path.join(root, file)
            all_files.append(full_path)
    return all_files

def extract_urls(text):
    """Extract URLs from a text string."""
    url_pattern = re.compile(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    )
    return url_pattern.findall(text)

# ========== Memory State ==========

FILE_HASHES = {}

# ========== Tools ==========

@tool
def get_project_context(_) -> str:
    """Returns current file structure."""
    structure = []
    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in {'.git', 'node_modules', '.env', '__pycache__'}]
        structure.append({"path": root, "dirs": dirs, "files": files})
    return json.dumps(structure, indent=2)

@tool
def get_changed_files(_) -> str:
    """Returns list and diffs of changed files since last check."""
    global FILE_HASHES
    changed = []
    files = get_all_files()
    for file in files:
        try:
            current_hash = hash_file(file)
            if file not in FILE_HASHES:
                FILE_HASHES[file] = current_hash
                continue
            if current_hash != FILE_HASHES[file]:
                with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.readlines()
                with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                    old_content = f.readlines()
                diff = difflib.unified_diff(old_content, content)
                changed.append({"file": file, "diff": ''.join(diff)})
                FILE_HASHES[file] = current_hash
        except Exception as e:
            continue
    return json.dumps(changed, indent=2)

@tool
def scrape_website(url: str) -> str:
    """Scrapes a business website and extracts details. Only use when a valid URL is provided."""
    import requests
    from bs4 import BeautifulSoup

    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string if soup.title else "No title"
        h1 = soup.find('h1')
        description = h1.text.strip() if h1 else "No H1 found"
        return json.dumps({"title": title, "description": description})
    except Exception as e:
        return str(e)

@tool
def run_python_tests(_) -> str:
    """Runs all Python unittests and returns output."""
    import subprocess
    try:
        result = subprocess.run(["python", "-m", "unittest", "discover"], capture_output=True, text=True)
        return result.stdout + result.stderr
    except Exception as e:
        return str(e)

@tool
def generate_docs(_) -> str:
    """Generates documentation from Python docstrings."""
    docs = {}
    for file in get_all_files():
        if file.endswith('.py'):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read()
                docs[file] = content[:1000]  # Sample
            except:
                continue
    return json.dumps(docs, indent=2)

@tool
def file_editor(instructions: str) -> str:
    """Edits files based on natural language instructions."""
    # Placeholder: integrate a codegen model like OpenAI + AST transformer
    return "Received instructions: " + instructions

# ========== Agent Setup ==========

tools = [
    get_project_context,
    get_changed_files,
    scrape_website,
    run_python_tests,
    generate_docs,
    file_editor
]

# Define the system prompt
system_prompt = """You are DevAgent, an intelligent, autonomous software engineer and development assistant.

You are capable of:
- Understanding and responding to natural and technical queries
- Acting as a senior software engineer
- Generating modern, idiomatic, and production-ready code
- Debugging and testing code
- Documenting code with professional standards
- Maintaining full awareness of project files, structure, changes, and constraints
- Searching the web for the latest documentation, packages, tools, and code patterns
- Scraping live websites for real-time data (but ONLY when a URL is explicitly provided)
- Staying current with best practices, language updates, and API versions

Behavior Guidelines:
- Always prefer the most current, community-accepted standards.
- When asked to generate code, verify syntax and approach.
- Only use the scrape_website tool when a valid URL is explicitly provided in the prompt.
- Be modular, professional, and clear in your responses.
"""

agent_executor = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    agent_kwargs={
        "prefix": system_prompt
    }
)

# ========== Entry Point ==========

def run_agent(user_prompt: str):
    # Check if the prompt contains any URLs
    urls = extract_urls(user_prompt)
    
    # If URLs are found, include this information in the prompt
    if urls:
        enhanced_prompt = f"The following prompt contains URLs that you may need to scrape: {urls}\n\n{user_prompt}"
    else:
        enhanced_prompt = f"The following prompt does not contain any URLs to scrape. Focus on project structure and code analysis.\n\n{user_prompt}"
    
    return agent_executor.run(enhanced_prompt)


if __name__ == "__main__":
    while True:
        query = input("\n🧠 Ask the agent: ")
        if query.lower() in {"exit", "quit"}:
            break
        result = run_agent(query)
        print("\n🔍 Result:\n", result)
