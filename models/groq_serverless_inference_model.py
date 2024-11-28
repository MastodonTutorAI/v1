from langchain_groq import ChatGroq


def get_groq_model(groq_api_key, model):
    """
    This function initializes and returns a Groq model using the provided API key and model ID.

    Args:
    - groq_api_key (str): The API key for Groq service.
    - model (str): The ID of the model to be used.

    Returns:
    - groq_chat (ChatGroq): The initialized ChatGroq object ready to be used.
    """
    if not groq_api_key or not model:
        raise ValueError("Both GROQ_API_KEY and MODEL_ID_GROQ must be set in the environment.")

    groq_chat = ChatGroq(groq_api_key=groq_api_key, model_name=model)
    return groq_chat