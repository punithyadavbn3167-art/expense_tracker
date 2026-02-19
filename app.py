from flask import Flask, render_template, request, redirect, url_for
import csv
from datetime import datetime
import os
import sqlite3
from flask import Flask, render_template


app = Flask(__name__)

FILE_NAME = "expenses.csv"

# Create CSV file if not exists
def create_file():
    if not os.path.exists(FILE_NAME):
        with open(FILE_NAME, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["ID", "Date", "Category", "Amount", "Description"])

create_file()

def init_db():
    conn = sqlite3.connect("expenses.db")
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Date TEXT,
        Category TEXT,
        Amount REAL,
        Description TEXT
    )
    """)

    conn.commit()
    conn.close()

# Read expenses
def read_expenses():
    expenses = []
    with open(FILE_NAME, "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            expenses.append(row)
    return expenses


# Write expenses
def write_expenses(expenses):
    with open(FILE_NAME, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["ID", "Date", "Category", "Amount", "Description"])
        writer.writeheader()
        writer.writerows(expenses)


# Home Page
@app.route("/")
def index():
    expenses = read_expenses()
    return render_template("index.html", expenses=expenses)


# Add Expense
@app.route("/add", methods=["GET", "POST"])
def add_expense():
    if request.method == "POST":
        expenses = read_expenses()

        # Generate unique ID safely
        if expenses:
            new_id = str(max(int(e["ID"]) for e in expenses) + 1)
        else:
            new_id = "1"

        new_expense = {
            "ID": new_id,
            "Date": datetime.now().strftime("%Y-%m-%d"),
            "Category": request.form["category"],
            "Amount": request.form["amount"],
            "Description": request.form["description"]
        }

        expenses.append(new_expense)
        write_expenses(expenses)

        return redirect(url_for("index"))

    return render_template("add_expense.html")


# Delete Expense
@app.route("/delete/<id>")
def delete_expense(id):
    expenses = read_expenses()
    expenses = [e for e in expenses if e["ID"] != id]
    write_expenses(expenses)
    return redirect(url_for("index"))


# Edit Expense
@app.route("/edit/<id>", methods=["GET", "POST"])
def edit_expense(id):
    expenses = read_expenses()
    expense = next((e for e in expenses if e["ID"] == id), None)

    if expense is None:
        return "Expense not found", 404

    if request.method == "POST":
        expense["Category"] = request.form["category"]
        expense["Amount"] = request.form["amount"]
        expense["Description"] = request.form["description"]

        write_expenses(expenses)
        return redirect(url_for("index"))

    return render_template("edit_expense.html", expense=expense)

@app.route("/summary")
def summary():
    expenses = read_expenses()

    total = 0
    category_data = {}

    for e in expenses:
        amount = float(e["Amount"])
        total += amount

        category = e["Category"]
        if category in category_data:
            category_data[category] += amount
        else:
            category_data[category] = amount

    category_total = list(category_data.items())

    return render_template(
        "summary.html",
        total=total,
        category_total=category_total
    )



if __name__ == "__main__":
    init_db()
    app.run(debug=True)
