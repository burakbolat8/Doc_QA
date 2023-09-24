
FROM ubuntu:latest

# Install system dependencies
RUN apt-get update && apt-get install -y gcc python3.10 \
    python3-pip \
    build-essential \
    curl \
    software-properties-common \
    git \
    wget 
    
# Set the working directory inside the container
WORKDIR /app

RUN mkdir ./models

RUN wget -N -P ./models https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGML/resolve/main/llama-2-7b-chat.ggmlv3.q8_0.bin

COPY repo .

ADD config ./config 

ADD data ./data

ADD key .

RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1

RUN python3 -m pip install --upgrade pip

RUN pip install -r requirements.txt

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

CMD ["streamlit", "run", "streamlit_app.py",  "--server.port=8501", "--server.address=0.0.0.0"]
