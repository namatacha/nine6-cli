import re
import termios
import tty
import shutil
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
from rich.panel import Panel
from rich.live import Live
from rich.control import Control
from rich import box
from pathlib import Path
from prompt_toolkit import prompt
from prompt_toolkit.styles import Style

custom_style = Style.from_dict({'prompt': 'white'})

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
    """---------PROGRAM FUNCTION------------"""
    
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
                       "Using openrouter api (https://openrouter.ai/)\n", 
                       f"{symbol.warning()}. Type --help for see all available commands\n"]
        
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
                print('\n' * 2)
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
    
   #about memory

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        try:
            Path("memory.json").touch()
        except Exception as e:
            print(f"\n{symbol.error()} Load Memory Error: {e}")
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
            print(f"{symbol.error} Save Memory Error: {e}")
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(memory, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"\n{symbol.error()} Save Memory Error: {e}")

def delete_memory():
    if os.path.exists(MEMORY_FILE):
        os.remove(MEMORY_FILE)
        print(f"{colors.green}Memory Cleared Successfuly!{colors.reset}")
    else:
        print(f"{symbol.warning()} No memory file exists!")
        
    #Getting response

def get_prompt():
    try:
        with open(PROMPT, "r", encoding="utf-8") as f:
            content = f.read().strip()
            return content
    except Exception as e:
        print(f"\n{symbol.error()} Prompt Error: {e}")
        print('\n' * 2)

def call_api(user, memory):
    try:
        if not api_key.strip():
            print(f"\n{symbol.error()} {anerror.api_error()} {anerror.api_error_empty()}")
            print('\n' * 2)
            return
        header = {
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": site_url,
            "X-Title": site_name,
            "Content-Type": "application/json"
        }
            
        messages = [{"role": "system", "content": get_prompt()}]
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
        print(f"{colors.red}{symbol.error()}{colors.reset} Error Calling API: {e}")
        print('\n' * 2)
    except KeyboardInterrupt:
        print(f"{colors.red}{symbol.error()}{colors.reset} Interrupted!")
        print('\n' * 2)
        
def get_live_boxed_input():
    user_input = ""
    sys.stdout.write("\033[?25l")
    
    cols, rows = shutil.get_terminal_size()

    sys.stdout.write(f"\033[1;{rows-3}r")
    
    while True:
        cols, rows = shutil.get_terminal_size()

        sys.stdout.write(f"\033[{rows-2};1H\033[J")
        
        input_panel = Panel(
            f"> {user_input}█", 
            border_style="white",
            expand=True,
            width=cols-1, 
            padding=(0, 1),
            box=box.SQUARE
        )
        
        with console.capture() as capture:
            console.print(input_panel, end="")
        
        sys.stdout.write(capture.get().strip('\n'))
        sys.stdout.flush()

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            char = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

        if char == '\r': break
        elif char in ('\x7f', '\x08'): user_input = user_input[:-1]
        elif char == '\x03':

            sys.stdout.write("\033[r\033[?25h\n")
            sys.exit(0)
        elif ord(char) >= 32: user_input += char

    sys.stdout.write("\033[r") 
    sys.stdout.write(f"\033[{rows-2};1H\033[J\033[?25h")
    sys.stdout.flush()
    return user_input

def display_footer_info():
    cols, _ = shutil.get_terminal_size()

    mit_text = f"{colors.bright_white}MIT License © 2026 nine6 project. Feel free to fork & modify.{colors.reset}"
    another_text = f"{colors.bright_white}Nine6 cli is still in alpha version, \n bugs may occur sometimes, contact m1stc@atomicmail.io to report bugs{colors.reset}"

    status_line = (
        f"{colors.cyan}●{colors.reset} Current version: Alpha 0.0.4\n"
        f"{colors.cyan}●{colors.reset} Codename: Zen\n"
        f"{colors.cyan}●{colors.reset} OS: {platform.system()} \n"
        f"{colors.cyan}●{colors.reset} Arch: {platform.machine()} \n"
        f"{colors.cyan}●{colors.reset} Logic: Trinity-AI \n"
        f"{colors.cyan}●{colors.reset} Environment: Production\n"
        f"{colors.cyan}●{colors.reset} Github: https://github.com/namatacha/nine6-cli\n"
    )

    print("\n") 
    print(status_line)
    print(another_text)
    print('\n')
    print(mit_text)

def main():
    func.clear()
    print(func.text_display())
    func.info()
    display_footer_info()
    memory = load_memory()
    while True:
        try:
            user = get_live_boxed_input()
            
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
                print('\n'* 2)
                continue
            
            if user.lower() == '/run':
                func.run()
                continue
            
            if user.lower() == '/key':
                func.print_key()
                print('\n' * 2)
                continue
            
            #double strip command

            if user.lower() == '--help':
                func.command(user)
                print('\n' * 2)
                continue

            if not user.strip():
                continue
            
            #response

            response = call_api(user, memory)
            

            if response:
                print(f"\n{colors.bright_white}Response:{colors.reset}\n")
                cleaned_response = re.sub(r'\*\*|###', '', response)
                smart_display(cleaned_response)
                print('\n' * 2)

                memory.append({"role": "user", "content": user})
                memory.append({"role": "assistant", "content": response})
                save_memory(memory)
            
        except Exception as e:
            print(f"\n{symbol.error()} Error Occured[main()]: {e}")
        except KeyboardInterrupt:
            continue

if __name__ == '__main__':
    main()
