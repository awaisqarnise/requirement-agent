from fastapi import FastAPI
from pydantic import BaseModel
from services.requirements_extractor import requirement_extractor
from services.validation import validate_project_description
from fastapi import HTTPException

# Initialize FastAPI app
app = FastAPI(
    title="Requirement Agent API",
    description="API for software project requirement analysis.",
    version="1.0",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc"  # Alternative Redoc UI
)


# Define request model
class ProjectRequest(BaseModel):
    project_description: str

@app.get("/")
def read_root():
    return {"message": "Welcome to the Requirement Analysis API!"}

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


