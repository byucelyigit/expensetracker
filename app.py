from flask import Flask, request, jsonify
from flask_cors import CORS
from utils.db_helper import expenses_container, budget_container
from utils.openai_helper import classify_expense
from datetime import datetime
import uuid

app = Flask(__name__)
CORS(app)

@app.route('/api/budget-items', methods=['GET', 'POST', 'PUT', 'DELETE'])
def manage_budget_items():
    if request.method == 'GET':
        query = "SELECT * FROM BudgetItems"
        items = list(budget_container.query_items(query=query, enable_cross_partition_query=True))
        return jsonify(items)
    
    elif request.method == 'POST':
        data = request.json
        if 'budgetCode' not in data or 'definition' not in data:
            return jsonify({"error": "budgetCode and definition are required"}), 400
        budget_container.create_item(body=data)
        return jsonify({"message": "Budget item created"}), 201
    
    elif request.method == 'PUT':
        data = request.json
        if 'budgetCode' not in data:
            return jsonify({"error": "budgetCode is required"}), 400
        try:
            item = budget_container.read_item(item=data['budgetCode'], partition_key=data['budgetCode'])
            item.update(data)
            budget_container.upsert_item(body=item)
            return jsonify({"message": "Budget item updated"}), 200
        except:
            return jsonify({"error": "Budget item not found"}), 404
    
    elif request.method == 'DELETE':
        data = request.json
        if 'budgetCode' not in data:
            return jsonify({"error": "budgetCode is required"}), 400
        try:
            budget_container.delete_item(item=data['budgetCode'], partition_key=data['budgetCode'])
            return jsonify({"message": "Budget item deleted"}), 200
        except:
            return jsonify({"error": "Budget item not found"}), 404

@app.route('/api/expenses', methods=['GET', 'POST', 'PUT', 'DELETE'])
def manage_expenses():
    if request.method == 'GET':
        query = "SELECT * FROM Expenses"
        expenses = list(expenses_container.query_items(query=query, enable_cross_partition_query=True))
        total = sum(expense['amount'] for expense in expenses if 'amount' in expense)
        return jsonify({"expenses": expenses, "total": total})
    
    elif request.method == 'POST':
        data = request.json
        if 'expenseText' not in data:
            return jsonify({"error": "expenseText is required"}), 400
        
        # Retrieve budget items
        budget_items = list(budget_container.query_items(query="SELECT * FROM BudgetItems", enable_cross_partition_query=True))
        
        # Classify expense using OpenAI
        classification = classify_expense(data['expenseText'], budget_items)
        if not classification:
            return jsonify({"error": "Failed to classify expense"}), 500
        
        # Handle missing date
        if not classification.get('date'):
            classification['date'] = datetime.utcnow().strftime('%Y-%m-%d')
        
        # Create expense record
        expense = {
            'id': str(uuid.uuid4()),
            'amount': classification.get('amount', 0.0),
            'date': classification.get('date'),
            'description': classification.get('description', ''),
            'budgetType': classification.get('budgetType', 'H01')  # Default to General Expenses
        }
        expenses_container.create_item(body=expense)
        return jsonify(expense), 201
    
    elif request.method == 'PUT':
        data = request.json
        if 'id' not in data:
            return jsonify({"error": "Expense id is required"}), 400
        try:
            expense = expenses_container.read_item(item=data['id'], partition_key=data['id'])
            expense.update(data)
            expenses_container.upsert_item(body=expense)
            return jsonify({"message": "Expense updated"}), 200
        except:
            return jsonify({"error": "Expense not found"}), 404
    
    elif request.method == 'DELETE':
        data = request.json
        if 'id' not in data:
            return jsonify({"error": "Expense id is required"}), 400
        try:
            expenses_container.delete_item(item=data['id'], partition_key=data['id'])
            return jsonify({"message": "Expense deleted"}), 200
        except:
            return jsonify({"error": "Expense not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
