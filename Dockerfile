FROM ollama/ollama

RUN echo "Installing the base dependencies..."
RUN DEBIAN_FRONTEND=noninteractive apt update && apt upgrade -y && apt install -y --no-install-recommends \
  vim \
  curl \
  tmux \
  python3 \
  python3-venv \
  git \
  && apt clean \
  && rm -rf /var/lib/apt/lists/*

RUN rm -rf ~/.ollama

#RUN mkdir /workdir
#RUN python3 -m venv /workdir/venv
#RUN /workdir/venv/bin/pip install --upgrade pip
#RUN /workdir/venv/bin/pip install open-interpreter

#ENTRYPOINT ["/workdir/venv/bin/interpreter", "-y", "--local"]
