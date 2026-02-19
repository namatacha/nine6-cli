import re
import requests
import json
import os
from dotenv import load_dotenv
import time
import sys
import platform
from datetime import datetime
from datetime import timedelta
from rich.console import Console
from rich.syntax import Syntax
from pathlib import Path

console = Console()

load_dotenv()

api_key = os.getenv("API_KEY")
site_url = os.getenv("SITE_URL")
site_name = os.getenv("SITE_NAME")
model = os.getenv("MODEL")
MEMORY_FILE = "memory.json"
PROMPT = "prompt.txt"
initial_data = None

def smart_display(text):
    parts = re.split(r'```(\w+)?\n?(.*?)```', text, flags=re.DOTALL)
    i = 0
    while i < len(parts):
        content = parts[i]

        if i % 3 == 0:
            if content.strip():
                typing_print(content)
            i += 1
        else:
            lang = parts[i] if parts[i] else "python"
            code_content = parts[i+1]
            syntax = Syntax(code_content.strip(), lang, theme="monokai", line_numbers=False)
            console.print(syntax)
            i += 2

class colors:
    black = "\033[0;30m"
    red = "\033[0;31m"
    green = "\033[0;32m"
    yellow = "\033[0;33m"
    blue = "\033[0;34m"
    purple = "\033[0;35m"
    cyan = "\033[0;36m"
    white = "\033[0;37m"
    bright_black = "\033[1;30m"
    bright_red = "\033[1;31m"
    bright_green = "\033[1;32m"
    bright_yellow = "\033[1;33m"
    bright_blue = "\033[1;34m"
    bright_purple = "\033[1;35m"
    bright_cyan = "\033[1;36m"
    bright_white = "\033[1;37m"
    reset = "\033[0m"
    bold = "\033[1m"

class func:
    def text_display():
        text = f'''

{colors.white}███╗░░██╗██╗███╗░░██╗███████╗{colors.purple}░█████╗░{colors.reset}
{colors.white}████╗░██║██║████╗░██║██╔════╝{colors.purple}██╔═══╝░{colors.reset}
{colors.white}██╔██╗██║██║██╔██╗██║█████╗{colors.purple}░░██████╗░{colors.reset}
{colors.white}██║╚████║██║██║╚████║██╔══╝{colors.purple}░░██╔══██╗{colors.reset}
{colors.white}██║░╚███║██║██║░╚███║███████╗{colors.purple}╚█████╔╝{colors.reset}
{colors.white}╚═╝░░╚══╝╚═╝╚═╝░░╚══╝╚══════╝{colors.purple}░╚════╝░{colors.reset}
         '''

        return text

    def info():
        information = [f"Welcome to {colors.bright_white}nine{colors.purple}6{colors.reset}!\n", "VER: Alpha 0.0.1\n", "[!]. Type --help for see all commands available"]

        for i in information:
            print(i)

    def clear():
        os.system('cls' if platform.system() == 'Windows' else 'clear')

    def time():
        current_time = datetime.now()
        formatted_time = current_time.strftime("%H:%M:%S")
        print(formatted_time)

    def command(value):
        if value not in ['--help', '--guide']:
            print("Please only input available value!")

        if value == '--help':
            help = ["\n'cls' for clear screen", "'q' for exit"]
            for i in help:
                print(i)


func.clear()

def typing_print(text, delay=0.005):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        try:
            Path("memory.json").touch()
        except Exception as e:
            print(f"Error occured(load_memory): {e}")
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def save_memory(memory):
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(memory, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error occured[1]: {e}")

def delete_memory():
    if not os.path.exists(MEMORY_FILE):
        print("No memory file detected!")
    if os.path.exists(MEMORY_FILE):
        os.remove(MEMORY_FILE)

def prompt():
    try:
        with open(PROMPT, "r", encoding="utf-8") as f:
            content = f.read().strip()
            return content
    except Exception as e:
        print(f"Error occured[2]: {e}")
    
def call_api(user, memory):

    header = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": site_url,
        "X-Title": site_name,
        "Content-Type": "application/json"
    }

    messages = [{"role": "system", "content": prompt()}]
    messages.extend(memory)
    messages.append({"role": "user", "content": user})

    data = {
        "model": model,
        "messages": messages
    }

    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers=header,
        json=data
    )
    response.raise_for_status()
    return response.json()['choices'][0]['message']['content']
    
def main():
    memory = load_memory()
    print(func.text_display())
    func.info()
    while True:
        try:
            user = input(f"\n{colors.red}@{colors.reset}> ")

            if user.lower() == 'q':
                sys.exit(0)

            if user.lower() == 'cls':
                os.system('cls' if platform.system() == 'Windows' else 'clear')
                print(func.text_display())
                func.info()
                continue

            if user.lower() == '/reset':
                delete_memory()
                continue

            if user.lower() == '--help':
                func.command(user)
                continue

            if not user.strip():
                continue
            
            response = call_api(user, memory)

            if response:
                print("\nResponse: \n")
                smart_display(response.replace("**", ""))

                memory.append({"role": "user", "content": user})
                memory.append({"role": "assistant", "content": response})
                save_memory(memory)
            
        except Exception as e:
            print(f"Error occured[3]: {e}")
        except KeyboardInterrupt:
            continue

if __name__ == '__main__':
    main()
    
