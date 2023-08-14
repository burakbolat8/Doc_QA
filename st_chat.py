import streamlit as st
import random
import time

c1.title("Simple chat")

# Initialize chat hitory
if "messages" not in c1.session_state:
    c1.session_state.messages = []

# Display chat messages from history on app rerun
for message in c1.session_state.messages:
    with c1.chat_message(message["role"]):
        c1.markdown(message["content"])

# Accept user input
if prompt := c1.chat_input("What is up?"):
    # Add user message to chat history
    c1.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with c1.chat_message("user"):
        c1.markdown(prompt)

    # Display assistant response in chat message container
    with c1.chat_message("assistant"):
        message_placeholder = c1.empty()
        full_response = ""
        assistant_response = random.choice(
            [
                "Hello there! How can I assist you today?",
                "Hi, human! Is there anything I can help you with?",
                "Do you need help?",
            ]
        )
        # Simulate stream of response with milliseconds delay
        for chunk in assistant_response.split():
            full_response += chunk + " "
            time.sleep(0.05)
            # Add a blinking cursor to simulate typing
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    # Add assistant response to chat history
    c1.session_state.messages.append({"role": "assistant", "content": full_response})