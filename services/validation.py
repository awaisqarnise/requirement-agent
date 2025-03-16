from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from services.environment import load_environment

def validate_project_description(project_description):
    """Use LLM to check if the input is a valid project description."""
    openai_api_key = load_environment()
    if not openai_api_key:
        print("ERROR: OpenAI API key is missing or not loaded correctly!")
    model = ChatOpenAI(temperature=0.0, model="gpt-4-turbo", openai_api_key=openai_api_key)

    validation_prompt = ChatPromptTemplate.from_template(
        """Determine if the input is a valid software project description.

        A valid project description should:
        - Clearly state the project's purpose.
        - Mention at least one key feature or function **OR** its intended role.
        - Indicate the target audience or industry.

        Examples of VALID descriptions:
        - "A web-based platform for online course management that allows students to enroll in courses, track progress, and communicate with instructors."
        - "An AI agent for banks that serves as a customer service representative, answering queries, processing transactions, and handling user complaints."
        - "A chatbot for e-commerce websites that helps customers find products and answers FAQs."

        Examples of INVALID descriptions:
        - "An app."
        - "Create a software."
        - ""

        If the input meets these conditions, respond with **only** 'VALID'. Otherwise, respond with **only** 'INVALID'.

        Input: {project_description}"""
    )

    message = validation_prompt.format_messages(project_description=project_description)
    response = model.invoke(message)
    return response.content.strip().upper() == "VALID"
