import openai
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

def classify_expense(expense_text, budget_items):
    prompt = f"""
    Extract the expense amount, date (if any), description, and determine the budget type based on the following budget items:

    Budget Items:
    {', '.join([f"{item['budgetCode']}: {item['definition']}" for item in budget_items])}

    Expense Text:
    "{expense_text}"

    Response Format:
    {
        "amount": <float>,
        "date": "<YYYY-MM-DD>",
        "description": "<description>",
        "budgetType": "<budgetCode>"
    }
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that extracts structured data from expense descriptions."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    result = response['choices'][0]['message']['content']
    # It's recommended to parse the JSON properly and handle exceptions
    import json
    try:
        return json.loads(result)
    except json.JSONDecodeError:
        # Handle parsing error, possibly return None or a default value
        return None
