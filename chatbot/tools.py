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
    raise FileNotFoundError(f"Couldn’t find 'premium.xlsx' at {EXCEL_FILE_PATH}. Please check the file path!")
except Exception as e:
    raise Exception(f"Error loading 'premium.xlsx': {str(e)}")

# Define unique values globally (Gender and Cancer types still hardcoded as they’re unlikely to change)
GENDER_UNIQUE = ['Male', 'Female']
CANCER_UNIQUE = ['Kidney Cancer', 'Lung Cancer', 'Throat Cancer', 'Skin Cancer',
                 'Thyroid Cancer', 'Cervical Cancer', 'Bone Cancer', 'Bladder Cancer']

@tool
def premium_filter(age: str, cancer: str, gender: str):
    """Retrieve premium details for different cancer types based on age, gender, and cancer type.

    Args:
        age (str): Age of the person (e.g., '15', '39', etc.)
        cancer (str): Type of cancer (e.g., 'Kidney Cancer')
        gender (str): Gender of the person ('Male' or 'Female')

    Returns:
        str: Formatted premium details or an error message if inputs are invalid.
    """
    global df, AGE_UNIQUE, GENDER_UNIQUE, CANCER_UNIQUE

    # Normalize inputs
    age = str(age).strip()
    gender = gender.strip().capitalize()
    cancer = cancer.strip().title()

    # Validate gender and cancer type
    if gender not in GENDER_UNIQUE:
        return "Hmm, gender should be 'Male' or 'Female'. Could you please specify?"
    if cancer not in CANCER_UNIQUE:
        return f"We cover these cancer types: {', '.join(CANCER_UNIQUE)}. Please pick one!"

    # Handle age dynamically
    try:
        age_int = int(age)  # Convert age to integer for comparison
        if age not in AGE_UNIQUE:
            # Find the closest age in the data
            closest_age = min(AGE_UNIQUE, key=lambda x: abs(int(x) - age_int))
            # Check if the closest age has data for this cancer and gender
            df_check = df[(df['Age'] == closest_age) & (df['Cancer_type'] == cancer) & (df['Gender'] == gender)]
            if df_check.empty:
                return f"Sorry, we don’t have premium data for {cancer} near age {age} for {gender}s. Try a different cancer type or gender?"
            return f"We don’t have exact data for age {age}, but here’s what we have for age {closest_age}:\n" + premium_filter(closest_age, cancer, gender)
    except ValueError:
        return f"Please enter a valid age (e.g., '15', '39'). I can work with ages like: {', '.join(AGE_UNIQUE)}."

    # Filter the DataFrame with error handling
    try:
        df_filter = df[(df['Age'] == age) & (df['Cancer_type'] == cancer) & (df['Gender'] == gender)]
    except Exception as e:
        return f"Sorry, something went wrong while fetching the data: {str(e)}. Let’s try again!"

    if df_filter.empty:
        return f"Sorry, no premium data is available for {cancer} at age {age} for {gender}s. Try different details?"

    # Format the premium details
    result = f"Great! Here are the premium options for {cancer} insurance (Age {age}, {gender}):\n"
    for _, row in df_filter.iterrows():
        result += f"- {row['Stage']}:\n"
        result += f"  • Option A: IDR {row['Option A']} – Top-tier coverage\n"
        result += f"  • Option B: IDR {row['Option B']} – Balanced choice\n"
        result += f"  • Option C: IDR {row['Option C']} – Budget-friendly\n"

    return result

# Define tools and ToolNode
tools = [premium_filter]
tool_node = ToolNode(tools)
#     global df, AGE_UNIQUE, GENDER_UNIQUE, CANCER_UNIQUE

#     if age not in AGE_UNIQUE or gender not in GENDER_UNIQUE or cancer not in CANCER_UNIQUE:
#         return ("Invalid input. Please provide valid details. Supported ages: 15, 20, 25, 30, 35, 40, 45, 50. "
#                 "Genders: Male, Female. Cancer types: Kidney Cancer, Lung Cancer, Throat Cancer, Skin Cancer, "
#                 "Thyroid Cancer, Cervical Cancer, Bone Cancer, Bladder Cancer.")

#     df_filter = df[(df['Age'] == age) & (df['Cancer_type'] == cancer) & (df['Gender'] == gender)]

#     if df_filter.empty:
#         return "No premium data available for the provided criteria."

#     result = f"Premium options for {cancer}, {gender}, Age {age}:\n"
#     for _, row in df_filter.iterrows():
#         result += f"- {row['Stage']}: Option A: IDR {row['Option A']}, Option B: IDR {row['Option B']}, Option C: IDR {row['Option C']}\n"

#     return result

# tools = [premium_filter]
# tool_node = ToolNode(tools)
