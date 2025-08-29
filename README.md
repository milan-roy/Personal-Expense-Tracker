
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
│── auth.py               # User registration and authentication
│── db.py                 # Database setup and all db functionalities
│── requirements.txt      # Dependencies
│── dashboard.py          # User dashboard
│── README.md             # Project documentation
```

---

## Installation

1. Clone the repo:
   ```bash
   git clone https://github.com/milan-roy/Personal-Expense-Tracker.git
   cd Personal-Expense-Tracker
   ```

2. Create a virtual environment & install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Mac/Linux
   venv\Scripts\activate      # On Windows
   pip install -r requirements.txt
   ```

3. Create a .env file in the project root and add your PostgreSQL connection string as 
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

| Date                | Type     | Category     | Amount | Currency | Memo       | Wallet                |
| ------------------- | -------- | ------------ | ------ | -------- | ---------- | --------------------- |
| 07/20/2025, 4:16 PM | Expense  | Food         | -40.00 | INR      | Memo 1     | Wallet 1              |
| 07/19/2025, 8:47 PM | Income   | Others       |  20.00 | INR      | Memo 2     | Wallet 2              |
| 07/19/2025, 8:36 PM | Expense  | Travel       | -25.00 | INR      | Memo 3     | Wallet 1 -> Wallet 2  |
| 07/18/2025, 8:08 PM | Transfer | Transfer     | -20.00 | INR      | Memo 4     | Wallet 1              |

---

