from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from services.environment import load_environment
from services.tech_stack import load_hourly_rates
from services.cost_calculator import attach_hourly_rates, calculate_cost

def requirement_extractor(project_description):
    """Extract project requirements and calculate cost estimation."""
    model = "gpt-4-turbo"
    openai_api_key = load_environment()

    # Corrected JSON structure
    prompt = """Extract the project requirements from the given project description.
    Provide the response in the following JSON format:

    
    json
    {{
        "frontend_requirements": ["Requirement 1", "Requirement 2"],
        "backend_requirements": ["Requirement 1", "Requirement 2"],
        "database_requirements": ["Requirement 1", "Requirement 2"],
        "total_number_of_resources_required": "Estimate based on project complexity",
        "suggested_tech_stack": [
            {{"technology": "Frontend Tech", "version": "Specify the most widely used version as of 2024", 
                "reason": "Specify the reason why you have chosen this technology stack"}},
            {{"technology": "Backend Tech", "version": "Specify the most widely used version as of 2024", 
                "reason": "Specify the reason why you have chosen this technology stack"}},
            {{"technology": "Database Tech", "version": "Specify the most widely used version as of 2024", 
                "reason": "Specify the reason why you have chosen this technology stack"}},
            {{"technology": "Cloud Tech", "version": "Specify the most widely used version as of 2024", 
                "reason": "Specify the reason why you have chosen this technology stack"}},
        ],
        "estimated_development_time": "Estimate in weeks",
        "team_roles": ["Frontend Developer", "Backend Developer", "UX Designer"],
        "cost_estimation": {{
            "total_cost": "Estimate total cost in USD",
            "frontend_cost": {{
                "estimated_hours": "Estimate total hours for frontend development",
                "hourly_rate": "Refer to the preconfigured hourly rate table for this technology",
                "subtotal": "Calculate frontend cost (hours * rate)"
            }},
            "backend_cost": {{
                "estimated_hours": "Estimate total hours for backend development",
                "hourly_rate": "Refer to the preconfigured hourly rate table for this technology",
                "subtotal": "Calculate backend cost (hours * rate)"
            }},
            "database_cost": {{
                "estimated_hours": "Estimate total hours for database design & setup",
                "hourly_rate": "Refer to the preconfigured hourly rate table for this technology",
                "subtotal": "Calculate database cost (hours * rate)"
            }},
            "other_costs": "Estimate additional costs such as hosting, infrastructure, third-party API usage."
        }},
        
        "project_plan": {{
            "planning_phase": "Describe planning activities",
            "development_phase": "Describe development activities",
            "testing_phase": "Describe testing activities",
            "deployment_phase": "Describe deployment activities"
        }},
        
        "milestone_plan": [
            {{"milestone": "MVP Launch", "expected_date": "Month 1"}},
            {{"milestone": "Beta Release", "expected_date": "Month 2"}},
            {{"milestone": "Full Release", "expected_date": "Month 3"}}
        ],
        
        "risk_assessment": [
            {{"risk": "Potential technical debt", "mitigation_strategy": "Ensure code reviews and best practices"}},
            {{"risk": "Scope creep", "mitigation_strategy": "Use agile methodology to manage requirements"}}
        ]
        
    }}


    Analyze the project description carefully and provide:

    Precise technology recommendations (React, Vue, Node.js, PostgreSQL, etc.).
    Actual version numbers used in production environments as of 2024.
    Ensure all technologies are compatible.
    ⚠️ DO NOT return generic placeholders like "Latest Stable Version". Instead, provide actual, widely used version numbers (e.g., "React 18.2.0", "Node.js 16.14.2").
    ⚠️ If multiple versions exist, choose the most recommended one for modern development.
    ⚠️ Give the reason why a particular tech stack is selected based on how widely it is used, the relvance to the project and the community support and edge of other similar technologies

    Project Description:
    {text}

    {format_instructions}
    """

    # Define schemas for structured output
    response_schemas = [
        ResponseSchema(name="frontend_requirements", 
                                    description="Enlist all frontend requirements"),
        ResponseSchema(name="backend_requirements",
                                    description="Enlist all backend requirements"),
        ResponseSchema(name="database_requirements",
                                    description="Enlist all database requirements"),
        ResponseSchema(name="total_number_of_resources_required",
                                    description="Enlist total number of resources required to complete this project"),
        ResponseSchema(name="suggested_tech_stack",
                                    description="Suggest the best technology stack based on project requirements, including the recommended version for each technology and the reason why it is selected"),
        ResponseSchema(name="estimated_development_time",
                                    description="Estimate the total development time in weeks"),
        ResponseSchema(name="team_roles",
                                    description="List the required team roles such as Frontend Developer, Backend Developer, UX Designer, etc"),
        ResponseSchema(name="cost_estimation",
                                    description="Provide cost estimation based on estimated hours and hourly rate."),  
        ResponseSchema(name="project_plan", 
                                    description="Provide a project plan with phases such as Planning, Development, Testing, and Deployment."),
        ResponseSchema(name="milestone_plan", 
                                    description="Provide key milestones such as MVP launch, Beta release, Full release."),
        ResponseSchema(name="risk_assessment", 
                                    description="Identify potential risks and challenges in the project."),
    ]

    structured_output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
    format_instructions = structured_output_parser.get_format_instructions()

    # prompt template
    prompt_template = ChatPromptTemplate.from_template(prompt)
    message = prompt_template.format_messages(
        text=project_description, format_instructions=format_instructions
    )
    
    # ChatOpenAI call
    llm = ChatOpenAI(temperature=0.0, model=model)
    response = llm.invoke(message)

    llm_response_text = response.content.strip()

    import json
    import re
    llm_response_text = re.sub(r"^```json\n|\n```$", "", llm_response_text)
    
    try:
        llm_response_dict = json.loads(llm_response_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON Parsing Error: {e} \nRaw LLM Response: {llm_response_text}")


    # Convert cleaned response to dictionary
    #llm_response_dict = json.loads(llm_response_text)

    hourly_rates = load_hourly_rates()
    updated_response = attach_hourly_rates(llm_response_dict)
    updated_response = calculate_cost(updated_response)

    return updated_response
