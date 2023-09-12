# Use the official Python 3.10 image as a parent image
FROM python:3.10-slim-buster

# Install system dependencies
RUN apt-get update && apt-get install -y gcc python3-dev


# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN python -m pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt

# Expose port 40017 for Streamlit
EXPOSE 40017

# Copy the rest of the files from your current directory to /app in the container
COPY . .

# Define the command to run your Streamlit app on port 40017
CMD ["streamlit", "run", "streamlit_app.py", "--server.port", "40017"]
