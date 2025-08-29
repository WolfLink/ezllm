from ollama import Chat
from tools import Tool

@Tool
def hello_world_tool(message):
    """
    Prints the specified message to the console. Returns "None" if successful.

    :param str message: The message to print.
    """
    print(f"Hello World! : {message}")

chat = Chat(model="gpt-oss:120b")
chat.add_tool(hello_world_tool)
#response = chat.prompt("Use the hello_world_tool to send a greeting message!")
#print(response)

#for message in chat.messages:
#    print(message)


from random import randint

@Tool
def roll_dice(number: int, sides: int) -> int:
    """
    Rolls multiple dice and computes the sum. Useful for board games and games like dungeons and dragons.

    :number: The number of dice to roll.
    :sides: The number of sides on the dice.
    """
    total = 0
    for _ in range(number):
        total += randint(1, sides)
    return total


chat.add_tool(roll_dice)
chat.system("Use your tools to inform your answer whenever possible!")
response = chat.prompt("I'm playing a dnd game. I cast fireball, which deals 2d6 damage! Does it kill the imp with 5 health left?")
print(response)

print("\n\n")

for message in chat.messages:
    print(message)
