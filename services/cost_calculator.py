from services.tech_stack import load_hourly_rates
def attach_hourly_rates(llm_response):
    """Fetch hourly rates for technologies returned by LLM."""
    print("🔍 Debugging attach_hourly_rates()...")  # Debugging message
    print("LMM Response Type:", type(llm_response))  # Should be a dictionary
    print("LMM Response Content:", llm_response)  # Check if it's correct

    # ✅ Load hourly rates from JSON file
    hourly_rates = load_hourly_rates()
    print("🔍 Loaded Hourly Rates:", hourly_rates)  # Debugging

    for tech in llm_response.get("suggested_tech_stack", []):
        tech_name = tech["technology"]
        print(f"🔍 Checking tech: {tech_name}")  # Debug each tech
        tech["hourly_rate"] = hourly_rates.get(tech_name, "Not Found")  # ✅ Uses dynamic rates

    print("✅ Updated Response:", llm_response)  # Check final result
    return llm_response

def calculate_cost(updated_response):
    """Calculate total cost dynamically based on hourly rates and estimated hours."""
    total_cost = 0

    cost_categories = ["frontend_cost", "backend_cost", "database_cost"]
    
    for category in cost_categories:
        if category in updated_response["cost_estimation"]:
            cost_data = updated_response["cost_estimation"][category]
            estimated_hours = int(cost_data.get("estimated_hours", "0").replace(",", ""))

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

            hourly_rate = next(
                (tech["hourly_rate"] for tech in updated_response["suggested_tech_stack"] if tech["technology"] == tech_name),
                "Not Found"
            )

            if isinstance(hourly_rate, (int, float)):
                subtotal = estimated_hours * hourly_rate
                cost_data["hourly_rate"] = f"${hourly_rate}"
                cost_data["subtotal"] = f"${subtotal:,}"
                total_cost += subtotal
                
    # ✅ Add Other Costs to Total Cost
    other_costs = updated_response["cost_estimation"].get("other_costs", "0")

    # 🔹 Extract numeric value from "other_costs" (it may be "$38,500 (includes...)" )
    import re
    match = re.search(r"(\d[\d,]*)", other_costs)  # Extracts "38,500"
    if match:
        other_cost_numeric = int(match.group(1).replace(",", ""))
        total_cost += other_cost_numeric  # ✅ Add to total
                
    updated_response["cost_estimation"]["total_cost"] = f"${total_cost:,}"
    return updated_response
