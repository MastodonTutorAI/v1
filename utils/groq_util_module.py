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
    def __init__(self, course_name, course_summary):
        self.course_name = course_name
        self.course_summary = course_summary
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

        Your goal is to provide context-driven, accurate responses that feel as though the professor is addressing the student.
        
        Below is course summary, what professor taught until now and what are the contents and some helpful keywords for you to understand context.
        
        {self.course_summary}
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

class GroqCorseSummarizer:
    def __init__(self, mongodb):
        self.groq_model = self.initialize_chatbot()
        self.mongodb = mongodb

    def initialize_chatbot(self):
        """Initialize the Groq chatbot."""
        return get_groq_model(groq_api_key, model)

    def get_system_prompt(self):
        """Construct the system prompt for the chatbot."""
        return """
        You are a summarizer for individual documents. Your task is to create a one-sentence summary of the provided document. Ensure the summary is concise, capturing all important details and key points.
        """
    
    def summarize_chunk(self, user_input):
        """Get a response from the Groq chatbot."""
        system_prompt = self.get_system_prompt()
        prompt = f"{system_prompt}\n\nQUESTION:\n{user_input}"
        response = self.groq_model.predict(prompt)
        return response

    def get_combine_system_prompt(self):
        """Construct the system prompt for the chatbot."""
        return """
        You are a summarizer for course materials. Your task is to combine a new document summary with an existing course summary to create a refined, updated course summary. Ensure that the new summary:
        - Preserves all relevant details from the previous course summary.
        - Incorporates key points from the new document summary.
        - Includes information on whether the materials contain homework or assignment-related content, specifying the assignments if present.
        - Provides a list of keywords relevant to the course for contextual understanding.

        The output should strictly follow this JSON format and do not include anything other than JSON in your response:
        {
            "Contents": "A concise but detailed summary of the course contents.",
            "Homework/Assignments": "Details about any homework or assignments included, or 'None' if not applicable.",
            "Assignment Details": "If assignment present then assignment headings",
            "Keywords": ["Keyword1", "Keyword2", ...] 
        }

        Keep the summary brief to avoid exceeding token limits, while retaining all essential details.
        """

    def summarize_course(self, summaries, existing_course_summary):
        system_prompt = self.get_combine_system_prompt()
        prompt = f"{system_prompt}\n\n EXISTING SUMMARY:\n{existing_course_summary} \n\nSUMMARIES:\n{summaries}"
        response = self.groq_model.predict(prompt)
        return response
    
    def save_course_summary(self, course_id, extracted_text, existing_course_summary):
        try:
            document_summary = self.summarize_chunk(extracted_text)
            course_summary = self.summarize_course(document_summary, existing_course_summary)
            print('Course Summary: ' + str(course_summary))
            if self.mongodb.set_course_summary(course_id, course_summary):
                print("Done save_course_summary")
            else:
                print("Failed save_course_summary")
        except Exception as e:
            print("Failed save_course_summary")
            print(e)