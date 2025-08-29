from pyllama.ollama import Chat
from pyllama.tools import Tool
import pytest
import json

chat = Chat(model="qwen3:32b")
#response = chat.prompt("Use the hello_world_tool to send a greeting message!")
#print(response)

#for message in chat.messages:
#    print(message)

@pytest.mark.parametrize("question,expected", [
    ("Are you a robot?", True),
    ("Are humans destroying the enviornment?", True),
    ("Is 5 an even number?", False),
    ("Is 97 a prime number?", True),
    ("Is `print 'hello world'` valid C++ code?", False),
    ])
@pytest.mark.parametrize("model", [
    "qwen3:32b",
    "qwen3:latest",
    "gpt-oss:120b",
    "gpt-oss:latest",
    "deepseek-r1:70b",
    "deepseek-r1:32b",
    ])
def test_bool(model, question,  expected):
    chat = Chat(model=model)
    response = chat.query(question, {"answer" : bool})
    try:
        response = json.loads(response)
    except:
        raise AssertionError(f"Model did not respond with correctly formatted JSON. Got {response} instead.")
    assert "answer" in response, f"Model did not respond with correctly formatted JSON. Got {response} instead."
    assert response["answer"] == expected, f"Model did not answer correctly."

