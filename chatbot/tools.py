import pandas as pd
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode
import os

# Correct the path to the Excel file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXCEL_FILE_PATH = os.path.join(BASE_DIR, "premium.xlsx")

# Load and normalize the premium data once at startup
try:
    df = pd.read_excel(EXCEL_FILE_PATH, sheet_name="Sheet1")
    # Convert to string and normalize
    df = df.astype(str)
    df['Age'] = df['Age'].str.strip()
    df['Cancer_type'] = df['Cancer_type'].str.strip().str.title()
    df['Stage'] = df['Stage'].str.strip()
    df['Gender'] = df['Gender'].str.strip().str.capitalize()
    df['Option A'] = df['Option A'].str.strip()
    df['Option B'] = df['Option B'].str.strip()
    df['Option C'] = df['Option C'].str.strip()
    # Dynamically get unique ages from the DataFrame
    AGE_UNIQUE = sorted(df['Age'].unique().tolist())  # Extract unique ages from data
except FileNotFoundError:
    raise FileNotFoundError(f"Couldn't find 'premium.xlsx' at {EXCEL_FILE_PATH}. Please check the file path!")
except Exception as e:
    raise Exception(f"Error loading 'premium.xlsx': {str(e)}")

# Define unique values globally (Gender and Cancer types still hardcoded as they’re unlikely to change)
GENDER_UNIQUE = ['Male', 'Female']
CANCER_UNIQUE = ['Kidney Cancer', 'Lung Cancer', 'Throat Cancer', 'Skin Cancer',
                 'Thyroid Cancer', 'Cervical Cancer', 'Bone Cancer', 'Bladder Cancer']

@tool
def premium_filter(age: str, cancer: str, gender: str, option: str = "A"):
    """It is used for getting premium of different types of cancer on the basis of Age, Gender, Type of Cancer and Stage.
    Input:
        Age: Age of Person (can be specific age like "23" or range like "20-25")
        Gender: Male or Female
        Cancer_type: Type of Cancer person is suffering from
        Option: Optional - A (Premium), B (Standard), or C (Basic) - defaults to A
    Output:
        Premium details and coverage options
    """
    global df, AGE_UNIQUE, GENDER_UNIQUE, CANCER_UNIQUE

    # Normalize inputs
    age = str(age).strip()
    gender = gender.strip().capitalize()
    cancer = cancer.strip().title()
    option = option.strip().upper()
    
    if option not in ["A", "B", "C"]:
        option = "A"  # Default to Premium plan
    
    option_column = f"Option {option}"
    
    # Map option to plan name and description
    option_details = {
        "A": {"name": "Premium", "desc_early": "provides extensive coverage for treatments, hospital stays, and specialized care"},
        "B": {"name": "Standard", "desc_early": "provides essential support for treatments and hospital stays at a moderate price"},
        "C": {"name": "Basic", "desc_early": "offers basic coverage for essential treatments at our most affordable rate"}
    }
    
    # Add descriptions for other stages
    for opt in option_details:
        option_details[opt]["desc_major"] = "offering balanced benefits for more intensive treatments and care"
        option_details[opt]["desc_advanced"] = "ensuring appropriate support for advanced treatments and hospitalizations"
    
    plan_name = option_details[option]["name"]

    # Validate gender and cancer type
    if gender not in GENDER_UNIQUE:
        return "I need to know if you're looking for coverage for a male or female. Could you please clarify?"
    if cancer not in CANCER_UNIQUE:
        return f"We provide coverage for {', '.join(CANCER_UNIQUE)}. Which type are you interested in?"

    # Map specific age to age range
    original_age = age  # Store the original age input
    if age not in AGE_UNIQUE:
        try:
            age_int = int(age)
            # Find the appropriate age range
            for age_range in AGE_UNIQUE:
                if "-" in age_range:
                    lower, upper = map(int, age_range.split("-"))
                    if lower <= age_int < upper:
                        age = age_range
                        break
            
            # If still not found, find closest
            if age not in AGE_UNIQUE:
                # Just use the first range that contains this age or is closest
                age = min(AGE_UNIQUE, key=lambda x: abs(int(x.split("-")[0]) - age_int))
        except ValueError:
            return f"Please provide a valid age. We have plans for these age groups: {', '.join(AGE_UNIQUE)}."

    # Filter the DataFrame with error handling
    try:
        df_filter = df[(df['Age'] == age) & (df['Cancer_type'] == cancer) & (df['Gender'] == gender)]
    except Exception as e:
        return f"I encountered an issue while retrieving your information. Let's try again with different details."

    if df_filter.empty:
        return f"I don't currently have coverage information for {cancer} at age {original_age} for {gender}s. Would you like to explore other options?"

    # Format the result based on the selected option
    result = f"For someone in your situation, we have several coverage options available for {cancer}. Let's look at the {plan_name} plan:\n\n"
    
    # Create a structured format that's easier for the agent to parse
    stages = {}
    for _, row in df_filter.iterrows():
        stage_name = row['Stage']
        stages[stage_name] = row[option_column]
    
    # Define the preferred order of stages
    preferred_order = ["Early Stage", "Major Stage", "Advanced Stage"]
    
    # Show all stages in the preferred order with the exact format requested
    for stage_name in preferred_order:
        if stage_name in stages:
            if stage_name == "Early Stage":
                result += f"- **{stage_name}**: The {plan_name} plan is IDR {stages[stage_name]}. It {option_details[option]['desc_early']}.\n"
            elif stage_name == "Major Stage":
                result += f"- **{stage_name}**: The {plan_name} plan is IDR {stages[stage_name]}, {option_details[option]['desc_major']}.\n"
            elif stage_name == "Advanced Stage":
                result += f"- **{stage_name}**: The {plan_name} plan is IDR {stages[stage_name]}, {option_details[option]['desc_advanced']}.\n"
    
    result += f"\nThis plan is designed to give you peace of mind, knowing that your medical expenses are covered, allowing you to focus on your recovery. Would you be interested in exploring this option further?"

    return result

# Define tools and ToolNode
tools = [premium_filter]
tool_node = ToolNode(tools)
