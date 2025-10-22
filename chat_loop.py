from ezllm import Chat
from rich.console import Console
from rich.markdown import Markdown

chat = Chat()
console = Console()

def chat_loop():
    try:
        while True:
            user = input("user: ")
            response = chat.prompt(user)
            print("agent: ")
            console.print(Markdown(response))
    except:
        print("\n\nChat exited.")

if __name__ == "__main__":
    chat_loop()
