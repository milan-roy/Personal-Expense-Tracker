
# Personal Expense Tracker

A **web-based expense tracker** built with **Streamlit**, **SQLAlchemy**, and **PostgreSQL**.  
It helps users manage personal finances by tracking income, expenses, and wallet transfers with ease.  

---

## Features
- **User Authentication** – Registration and login system.  
- **Wallets** – Create multiple wallets with an initial balance.  
- **Transactions** – Add income, expenses, or transfers between wallets with category, note, and datetime.  
- **CSV Upload** – Bulk import transactions from a predefined CSV format.  
- **Analytics Dashboard** – Interactive charts to visualize:  
  - Monthly income and expenses  
  - Expenses by category  
  - Wallet balances  

---

## Tech Stack
- [Streamlit](https://streamlit.io/) – frontend/dashboard  
- [SQLAlchemy](https://www.sqlalchemy.org/) – ORM for database management  
- [PostgreSQL](https://www.postgresql.org/) – backend database  
- [Pandas](https://pandas.pydata.org/) – data handling  
- [Plotly](https://plotly.com/python/) – data visualization  

---

## Project Structure
```
expense-tracker/
│── app.py                # Main Streamlit app
│── models.py             # Database models (SQLAlchemy)
│── db_setup.py           # Database setup script
│── requirements.txt      # Dependencies
│── data/
│   └── sample.csv        # Example transaction file
│── README.md             # Project documentation
```

---

## Installation

1. Clone the repo:
   ```bash
   git clone https://github.com/<your-username>/expense-tracker.git
   cd expense-tracker
   ```

2. Create a virtual environment & install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Mac/Linux
   venv\Scripts\activate      # On Windows
   pip install -r requirements.txt
   ```

3. Set up PostgreSQL and update your **database URL** in `db_setup.py`:
   ```python
   DATABASE_URL = "postgresql://username:password@localhost/expense_tracker"
   ```

4. Run the app:
   ```bash
   streamlit run app.py
   ```

---

## 📊 CSV Format
The uploaded CSV should follow this format:

| type     | amount | category | note         | datetime            |
|----------|--------|----------|--------------|---------------------|
| income   | 5000   | Salary   | March Salary | 2025-03-01 10:00:00 |
| expense  | 1200   | Food     | Groceries    | 2025-03-03 18:30:00 |
| transfer | 2000   | Wallet   | To savings   | 2025-03-05 12:00:00 |

---

