from colorama import Fore, Style, init

init(autoreset=True)

def red(text):     return f"{Fore.RED}{text}{Style.RESET_ALL}"
def green(text):   return f"{Fore.GREEN}{text}{Style.RESET_ALL}"
def yellow(text):  return f"{Fore.YELLOW}{text}{Style.RESET_ALL}"
def cyan(text):    return f"{Fore.CYAN}{text}{Style.RESET_ALL}"
def white(text):   return f"{Fore.WHITE}{Style.BRIGHT}{text}{Style.RESET_ALL}"
def gray(text):    return f"{Fore.WHITE}{text}{Style.RESET_ALL}"
def magenta(text): return f"{Fore.MAGENTA}{text}{Style.RESET_ALL}"

def ok(text):      return green(f"  [+] {text}")
def err(text):     return red(f"  [!] {text}")
def info(text):    return cyan(f"  [*] {text}")
def warn(text):    return yellow(f"  [~] {text}")
def dim(text):     return gray(f"      {text}")
