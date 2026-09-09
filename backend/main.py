from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from database import Base, engine, SessionLocal, Expense as ExpenseModel
#bring fastapi into my program
app = FastAPI()

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    return db

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Expense(BaseModel):
    name: str
    amount: int
@app.get("/")
#when  a GET request is sent to /,run the func underneath
def home():
    return {"message": "Expense Tracker API"}

@app.post("/expenses")
def add_expense(expense: Expense):
    db = get_db()

    new_expense = ExpenseModel(
        name=expense.name,
        amount=expense.amount
    )

    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)

    db.close()

    return {
        "message": "Expense added",
        "expense": {
            "id": new_expense.id,
            "name": new_expense.name,
            "amount": new_expense.amount
        }
    }

@app.get("/expenses")
def view_expenses():
    db = get_db()

    expenses = db.query(ExpenseModel).all()

    db.close()

    return {
        "expenses": [
            {
                "id": expense.id,
                "name": expense.name,
                "amount": expense.amount
            }
            for expense in expenses
        ]
    }

@app.delete("/expenses/{expense_id}")
def delete_expense(expense_id: int):
    db = get_db()

    expense = db.query(ExpenseModel).filter(
        ExpenseModel.id == expense_id
    ).first()

    if expense:
        db.delete(expense)
        db.commit()
        db.close()

        return {
            "message": "Expense deleted",
            "deleted": {
                "id": expense.id,
                "name": expense.name,
                "amount": expense.amount
            }
        }

    db.close()

    return {"message": "Invalid expense number"}

@app.put("/expenses/{expense_id}")
def edit_expense(expense_id: int, expense: Expense):
    db = get_db()

    existing_expense = db.query(ExpenseModel).filter(
        ExpenseModel.id == expense_id
    ).first()

    if existing_expense:
        existing_expense.name = expense.name
        existing_expense.amount = expense.amount

        db.commit()
        db.refresh(existing_expense)
        db.close()

        return {
            "message": "Expense updated",
            "expense": {
                "id": existing_expense.id,
                "name": existing_expense.name,
                "amount": existing_expense.amount
            }
        }

    db.close()

    return {"message": "Invalid expense number"}
@app.get("/expenses/total")
def total_expenses():
    db = get_db()

    expenses = db.query(ExpenseModel).all()

    total = 0

    for expense in expenses:
        total = total + expense.amount

    db.close()

    return {"total_expenses": total}