# Use the official Python 3.10 image as a parent image
FROM python:3.10-slim-buster

# Install system dependencies
RUN apt-get update && apt-get install -y gcc python3-dev \
    git \
    wget 


# Set the working directory inside the container
WORKDIR /app

RUN mkdir ./models

RUN wget -N -P ./models https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGML/resolve/main/llama-2-7b-chat.ggmlv3.q8_0.bin

RUN git clone https://github.com/burakbolat8/Doc_QA.git 

RUN mv ./Doc_QA/* ./app/

RUN python -m pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app.py", "--server.port", "8501"]
