from fastapi import FastAPI
from pydantic import BaseModel
from services.requirements_extractor import requirement_extractor
from services.validation import validate_project_description
from fastapi import HTTPException

# Initialize FastAPI app
app = FastAPI()

# Define request model
class ProjectRequest(BaseModel):
    project_description: str

@app.post("/analyze")
def analyze_project(request: ProjectRequest):
    # Use LLM to validate input
    if not validate_project_description(request.project_description):
        return {"message": "❌ The input doesn't seem like a project description. Please enter a valid project idea."}

    # If valid, proceed with requirement extraction
    try:
        result = requirement_extractor(request.project_description)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

    return result

