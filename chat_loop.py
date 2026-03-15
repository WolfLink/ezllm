from ezllm import Chat, attachments
from rich.console import Console
from rich.markdown import Markdown

chat = Chat()
console = Console()

def chat_loop():
    try:
        while True:
            user = input("user: ")
            # check for attachments:
            segments = user.split("!attach: ")
            user = segments[0]
            images = None
            if len(segments) > 1:
                images = []
                for segment in segments[1:]:
                    images.append(segment)

            response = chat.prompt(user, images=images)
            print("agent: ")
            console.print(Markdown(response))
    except:
        print("\n\nChat exited.")
        raise

if __name__ == "__main__":
    chat_loop()
