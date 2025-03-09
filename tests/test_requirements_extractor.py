import sys
sys.path.append(".")
from services.requirements_extractor import requirement_extractor

# Sample project description for testing
project_description = "I need a mobile app for my e-commerce store with a payment gateway, inventory management, and customer chat support."

# Run the function and print the response
result = requirement_extractor(project_description)
print(result)