#docker build . -t "open-interpreter"
#docker run --rm -it --runtime=nvidia --gpus all "open-interpreter"
docker run -d -v $(pwd)/ollama_home:/root/.ollama -p 11434:11434 --rm --gpus all --name ollama ollama/ollama
#docker exec -it ollama bash
#docker stop ollama
