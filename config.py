def calculate_cost(updated_response):
    """Dynamically calculate cost based on hourly rates and estimated hours."""
    total_cost = 0
    
    # Check if the cost estimation field exists
    if "cost_estimation" not in updated_response:
        updated_response["cost_estimation"] = {}

    # Define categories for cost estimation
    cost_categories = ["frontend_cost", "backend_cost", "database_cost"]
    
    for category in cost_categories:
        if category in updated_response["cost_estimation"]:
            cost_data = updated_response["cost_estimation"][category]

            # Convert estimated hours to integer
            estimated_hours = int(cost_data.get("estimated_hours", "0").replace(",", ""))

            # Dynamically find the most relevant technology
            tech_name = None
            for tech in updated_response["suggested_tech_stack"]:
                tech_lower = tech["technology"].lower()
                
                if "frontend" in category and any(word in tech_lower for word in ["react", "vue", "angular"]):
                    tech_name = tech["technology"]
                    break
                elif "backend" in category and any(word in tech_lower for word in ["node", "django", "flask", "spring"]):
                    tech_name = tech["technology"]
                    break
                elif "database" in category and any(word in tech_lower for word in ["postgres", "mysql", "mongodb"]):
                    tech_name = tech["technology"]
                    break

            # Dynamically get the hourly rate
            hourly_rate = next(
                (tech["hourly_rate"] for tech in updated_response["suggested_tech_stack"] if tech["technology"] == tech_name),
                "Not Found"
            )

            # If hourly rate is valid, calculate cost
            if isinstance(hourly_rate, (int, float)):
                subtotal = estimated_hours * hourly_rate
                cost_data["hourly_rate"] = f"${hourly_rate}"
                cost_data["subtotal"] = f"${subtotal:,}"
                total_cost += subtotal
                
    # Update total cost
    updated_response["cost_estimation"]["total_cost"] = f"${total_cost:,}"
    return updated_response

def validate_project_description(project_description):
    from langchain_openai import ChatOpenAI
    from langchain.prompts import ChatPromptTemplate
    import openai
    openai.api_key = load_environment()
    """Use LLM to check if the input is a valid project description."""
    model = ChatOpenAI(temperature=0.0, model="gpt-4-turbo")
    

    validation_prompt = ChatPromptTemplate.from_template(
        "Determine if the following input is a valid software project description. "
        "If yes, respond with 'VALID'. If not, respond with 'INVALID'.\n\n"
        "Input: {project_description}"
    )

    message = validation_prompt.format_messages(project_description=project_description)
    response = model.invoke(message)

    return response.content.strip().upper() == "VALID"

def requirement_extractor(project_description):
    from langchain_openai import ChatOpenAI
    from langchain.prompts import ChatPromptTemplate
    from langchain.output_parsers import ResponseSchema, StructuredOutputParser
    import openai

    model = "gpt-4-turbo"

    openai.api_key = load_environment()

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


    #print("Raw LLM Response:", response)
    #print("Raw LLM Content:", response.content)
    #print("-----------------------------------------------------")
    #exit(0)

    import json
    import re
    llm_response_text = response.content.strip()
    llm_response_text = re.sub(r"^json\n|\n$", "", llm_response_text)  # Remove backticks

    # ✅ Step 5: Convert cleaned response to dictionary
    llm_response_dict = json.loads(llm_response_text)

    # ✅ Step 6: Process response and attach hourly rates
    updated_response = attach_hourly_rates(llm_response_dict)
    updated_response = calculate_cost(updated_response)  # 🔹 Calculate dynamic cost


    return updated_response
    #print(updated_response)
    #exit(0)

    # response parsing
    #structured_response = structured_output_parser.parse(updated_response)

    #return structured_response