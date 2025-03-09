from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from services.environment import load_environment

def validate_project_description(project_description):
    """Use LLM to check if the input is a valid project description."""
    openai_api_key = load_environment()
    model = ChatOpenAI(temperature=0.0, model="gpt-4-turbo", openai_api_key=openai_api_key)

    validation_prompt = ChatPromptTemplate.from_template(
        "Determine if the following input is a valid software project description. "
        "If yes, respond with 'VALID'. If not, respond with 'INVALID'.\n\n"
        "Input: {project_description}"
    )

    message = validation_prompt.format_messages(project_description=project_description)
    response = model.invoke(message)

    return response.content.strip().upper() == "VALID"
