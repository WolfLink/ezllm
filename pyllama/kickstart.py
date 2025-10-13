import os
from .containers import Container

OLLAMA_DIR = "~/.ollama"
if "OLLAMA_MODELS" in os.environ:
    OLLAMA_DIR = os.path.abspath(os.environ["OLLAMA_MODELS"])
    try:
        OLLAMA_DIR = os.path.dirname(OLLAMA_DIR)
    except:
        pass

def kickstart(ollama_dir=None):
    if ollama_dir is None:
        ollama_dir = OLLAMA_DIR
    ollama_dir = os.path.abspath(ollama_dir)
    container = Container("ollama", "ollama/ollama", ports=[11434], volumes=[f"{ollama_dir}:/root/.ollama"])
    return container
