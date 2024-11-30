import os
from dotenv import load_dotenv
from models.groq_serverless_inference_model import get_groq_model
from langchain.chains import LLMChain
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.messages import SystemMessage
from langchain.chains.conversation.memory import ConversationBufferWindowMemory

# Load environment variables from .env file
load_dotenv()

groq_api_key = os.getenv('GROQ_API_KEY')
model = os.getenv('MODEL_ID_GROQ')
conversational_memory_length = 5

class GroqConversationManager:
    def __init__(self, course_name):
        self.course_name = course_name
        self.conversation_chain = None
        self.initialize_conversation_chain()
    
    def initialize_conversation_chain(self):
        self.conversation_chain = self.get_conversation()
    
    def load_conversation_history(self, messages):
        self.conversation_chain.memory.clear()
        
        for i in range(0, len(messages)-1, 2):
            if i+1 < len(messages):
                user_msg = messages[i]
                assistant_msg = messages[i+1]
                
                if user_msg["role"] == "user" and assistant_msg["role"] == "assistant":
                    self.conversation_chain.memory.chat_memory.add_user_message(user_msg["content"])
                    self.conversation_chain.memory.chat_memory.add_ai_message(assistant_msg["content"])

    def get_response(self, user_input, context, selected_conversation=None):
        if selected_conversation is not None:
            conversation_messages = selected_conversation.get("conversation", [])
            self.load_conversation_history(conversation_messages)
        
        # Create prompt using context and user input
        prompt = self.create_prompt(context, user_input)
        print(prompt)
        response = self.conversation_chain.predict(human_input=prompt)
        return response

    def create_prompt(self, context, user_input):
        """Create a prompt by combining context and user input."""
        prompt = f"CONTEXT\n\n {context}\n\n Question\n\n {user_input}"
        return prompt

    def clear_history(self):
        self.initialize_conversation_chain()

    def initialize_chatbot(self):
        """Initialize the Groq chatbot."""
        groq_chat = get_groq_model(groq_api_key, model)
        return groq_chat

    def get_system_prompt(self):
        """Construct the system prompt for the chatbot."""
        system_prompt = f"""
        You will be acting as a professor's assistant for the graduate-level course named '{self.course_name}'. 
        Your primary responsibility is to answer students' questions about course content with clarity, as if the professor were addressing the question directly in a classroom setting.

        Here are the critical rules for your interaction:
        1. Answer questions in a conversational, humanized manner, emulating the teaching style of a professor. Be supportive, engaging, and clear.
        2. Prioritize the provided course material to ensure responses align closely with the professor's teachings. If context is incomplete, supplement with your knowledge, but keep it course-relevant.
        3. If a question or word is not related to the course material or context, do not answer based on the course material. Only provide responses related to {self.course_name}.
        4. Break down complex {self.course_name} topics into simple, relatable explanations. Use examples, analogies, and step-by-step guidance to clarify difficult concepts.
        5. Approach each question respectfully, as if asked directly by a student to the professor. Your responses should be informative, helpful, and patient, especially when students may be struggling with challenging material.
        6. When appropriate, encourage deeper understanding and curiosity in students. Avoid overly technical jargon, but explain key terms in an accessible way.

        Your goal is to provide context-driven, accurate responses that feel as though the professor is addressing the student, fostering understanding in {self.course_name} topics.
        """
        return system_prompt

    def create_memory_indexing(self, conversational_memory_length):
        """Create memory for the conversation."""
        memory = ConversationBufferWindowMemory(k=conversational_memory_length, memory_key="chat_history", return_messages=True)
        return memory

    def build_prompt_question(self):
        """Construct the prompt template for generating responses."""
        prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content=self.get_system_prompt()
                ),
                MessagesPlaceholder(
                    variable_name="chat_history"
                ),
                HumanMessagePromptTemplate.from_template(
                    "{human_input}"
                ),
            ]
        )
        return prompt

    def get_conversation(self):
        """Create and return a conversation chain."""
        conversation = LLMChain(
            llm=self.initialize_chatbot(),  # Groq LangChain chat object
            prompt=self.build_prompt_question(),  # Constructed prompt
            verbose=False,  # Disable verbose output
            memory=self.create_memory_indexing(conversational_memory_length),  # Conversational memory
        )
        return conversation

    def generate_response(self, conversation, user_question):
        """Generate a response based on user input."""
        response = conversation.predict(human_input=user_question)
        return response

    def update_chat_history(self, messages, role, content):
        """Update chat history with new content."""
        messages.append({"role": role, "content": content})
        return messages

    def display_conversation(self, messages):
        """Display the conversation in a user-friendly format."""
        for message in messages:
            role = "🧑‍💻 User" if message["role"] == "user" else "🤖 Personal Bot"
            print(f"{role}: {message['content']}\n")