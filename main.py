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
    
class symbol:
    def warning():
        sym_warn = f"{colors.yellow}[!]{colors.reset}"
        return sym_warn
    
    def error():
        sym_err = f"{colors.red}[-!]{colors.reset}"
        return sym_err
    
    def asking():
        sym_ask = f"{colors.blue}[?]{colors.reset}"
        return sym_ask
    
class error:
    def __init__(self):
        self.api_error_msg = f"{colors.red}API_ERROR: {colors.reset}"
        self.api_error_empty_msg = "Oops, your api key is empty, please get the api key at https://openrouter.ai/"
        self.interrupt_msg = f"{colors.red}Interrupted!{colors.reset}"
        
    #----- API ERROR MESSAGES ------#
        
    def api_error(self):
        try:
            return self.api_error_msg
        except Exception as e:
            return f"{e}"
        
    def api_error_empty(self):
        try:
            return self.api_error_empty_msg
        except Exception as e:
            return f"{e}"
        
    #another
    
    def interrupt(self):
        try:
            return self.interrupt_msg
        except Exception as e:
            return f"{e}"
        
#call error class with var
anerror = error()

class func:
    """
    PROGRAM FUNCTION
    """
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
        #This line contain the info displayed below the nine6 logo
        information = [f"Welcome to {colors.bright_white}nine{colors.purple}6{colors.reset}!\n", 
                       "VER: Alpha 0.3", 
                       "Using openrouter api (https://openrouter.ai/)\n", 
                       f"{symbol.warning()}. Type --help for see all available commands"]
        
        for i in information:
            print(i)

    def clear():
        os.system('cls' if platform.system() == 'Windows' else 'clear')

    def time():
        current_time = datetime.now()
        formatted_time = current_time.strftime("%H:%M:%S")
        print(formatted_time)

    def command(value):
        if value not in ['--help', 
                         '--guide']:
            print("Please only input available value!")
            
        if value == '--help':
            help = ["\n'cls' for clear screen", 
                    "'q' for exit\n", 
                    "____*commands*_____", 
                    "\n/reset - reset the ai memory", 
                    "\n/run - to run program command"]
            
            for i in help:
                print(i)
                
    def run():
        command = input("\nrun system command > ")
        os.system(command)
        
    def debug(user, memory):
        try:
            if not api_key.strip():
                print(f"{symbol.error()} {anerror.api_error()} {anerror.api_error_empty()}")
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
            
            with console.status(" [DEBUG]Thinking...", spinner="dots"):
                response = requests.post(
                    url="https://openrouter.ai/api/v1/chat/completions",
                    headers=header,
                    json=data
                )
                
                print(f"\n{colors.green}API:{colors.reset} {api_key[:20]}" if not api_key.strip() else f"\n{colors.red}API key was empty!{colors.reset}")
                print(f"{colors.green}SITE_URL:{colors.reset} {site_url}")
                print(f"{colors.green}SITE_NAME:{colors.reset} {site_name}")
                print(f"{colors.green}USING MODEL:{colors.reset} {model}")
                
                response.raise_for_status()
                return response.json()['choices'][0]['message']['content']
            
        except Exception as e:
            print(f"{symbol.error()} Error occured[Debugged]:{colors.reset} {e}")
        except KeyboardInterrupt:
            print(f"{symbol.error()} {anerror.interrupt()}")
            
    def print_key():
        key = api_key
        print(f"\nYour api: {key[:20]}...")

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
            print(f"\n{symbol.error()}. Error occured(load_memory): {e}")
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def save_memory(memory):
    if not os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "w", encoding="utf-8") as f:
                json.dump(memory, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"{symbol.error}. Error occured[-1]: {e}")
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(memory, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"\n{symbol.error()}. Error occured[1]: {e}")

def delete_memory():
    if os.path.exists(MEMORY_FILE):
        os.remove(MEMORY_FILE)
        print(f"{colors.green}Memory Cleared Successfuly!{colors.reset}")
    else:
        print(f"{symbol.warning()}. No memory file exists!")

def prompt():
    try:
        with open(PROMPT, "r", encoding="utf-8") as f:
            content = f.read().strip()
            return content
    except Exception as e:
        print(f"\n{symbol.error()}. Error occured[2]: {e}")

def call_api(user, memory):
    try:
        if not api_key.strip():
            print(f"\n{symbol.error()} {anerror.api_error()} {anerror.api_error_empty()}")
            return
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
        
        with console.status(" Thinking...", spinner="dots"):
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers=header,
                json=data
            )
            
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    
    except Exception as e:
        print(f"{colors.red}{symbol.error()}{colors.reset}. Error Occured(call_api): {e}")
    except KeyboardInterrupt:
        print(f"{colors.red}{symbol.error()}{colors.reset}. Interrupted!")

def main():
    func.clear()
    memory = load_memory()
    print(func.text_display())
    func.info()
    while True:
        try:
            user = input(f"\n{colors.red}@{colors.reset}> ")
            
            #basic command

            if user.lower() == 'q':
                print(f"{colors.red}Exiting...{colors.reset}\n")
                sys.exit(0)

            if user.lower() == 'cls':
                os.system('cls' if platform.system() == 'Windows' else 'clear')
                print(func.text_display())
                func.info()
                continue
            
            #slash command
            
            if user.lower() == '/debug':
                user = input(f"{colors.green}@{colors.reset}> ")
                response = func.debug(user, memory)
                
                if response:
                    print(f"\n{colors.bright_white}Response[Debug]:{colors.reset}\n")
                    cleaned_response = re.sub(r'\*\*|###', '', response)
                    smart_display(cleaned_response)
                    
                    memory.append({"role": "user", "content": user})
                    memory.append({"role": "assistant", "content": response})
                    save_memory(memory)
                continue

            if user.lower() == '/reset':
                delete_memory()
                continue
            
            if user.lower() == '/run':
                func.run()
                continue
            
            if user.lower() == '/key':
                func.print_key()
                continue
            
            #double strip command

            if user.lower() == '--help':
                func.command(user)
                continue

            if not user.strip():
                continue
            
            #response

            response = call_api(user, memory)

            if response:
                print(f"\n{colors.bright_white}Response:{colors.reset}\n")
                cleaned_response = re.sub(r'\*\*|###', '', response)
                smart_display(cleaned_response)

                memory.append({"role": "user", "content": user})
                memory.append({"role": "assistant", "content": response})
                save_memory(memory)
            
        except Exception as e:
            print(f"\n{symbol.error()}. Error occured[3]: {e}")
        except KeyboardInterrupt:
            continue

if __name__ == '__main__':
    main()
