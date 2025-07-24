import streamlit as st
from sqlalchemy.orm import joinedload
from db import Session,add_wallet, add_transaction,edit_transaction,delete_transaction,import_transactions
from models import User, Wallet, Transaction
from decimal import Decimal
from streamlit_card import card
import datetime
import pandas as pd
from collections import defaultdict
import plotly.graph_objects as go

def wallets_tab(user):
    if len(user.wallets)==0:
            st.text("You have no wallets")
    else:
        sorted_wallets = sorted(user.wallets, key=lambda w: w.id)
        if "has_clicked" not in st.session_state:
            st.session_state.has_clicked = None
        for i in range(0, len(sorted_wallets), 2):
            cols = st.columns(2)  
            for j in range(2):
                if i + j < len(sorted_wallets):
                    wallet = sorted_wallets[i + j]
                    with cols[j]:
                        with st.container():
                            has_clicked = card(
                                title=wallet.name,
                                text="₹ " + str(wallet.amount) if wallet.type=='General' else "₹ -" + str(wallet.amount),
                                styles={
                                            "card": {
                                                "width": "120%",
                                                "height": "200%",
                                                "box-shadow": "0 0 10px rgba(0,0,0,0.5)",
                                                
                                            },
                                }
                            )
                            if has_clicked:
                                st.session_state.has_clicked = wallet.id


    if 'show_add_wallet_form' not in st.session_state:
        st.session_state.show_add_wallet_form = False

    if st.button("Add Wallet", key='addWallet'):
        st.session_state.show_add_wallet_form = True

    if st.session_state.show_add_wallet_form:
        st.markdown("### Add Wallet")
        with st.form("add_wallet_form"):
            name = st.text_input("Name")
            cols = st.columns(2)
            with cols[0]:
                amount = st.number_input(label="Initial Amount", min_value=0.00, value=0.00,step=0.01)
                amount = Decimal(str(amount)) 
            with cols[1]:
                type = st.selectbox('Select the type of wallet',['General','Credit Card'])

            cols = st.columns(2)
            with cols[0]:
                submit = st.form_submit_button("Submit")
            with cols[1]:
                cancel = st.form_submit_button("Cancel")

        if submit:
            add_wallet(user.id, name, amount, type)
            st.session_state.show_add_wallet_form = False
            st.rerun()

        if cancel:
            st.session_state.show_add_wallet_form = False
            st.rerun()

def transactions_form(user, type, categories=None, transaction=None,):
    is_editing = transaction is not None
    form_key = f"{'edit' if is_editing else 'add'}_{type}_form_{transaction.id if is_editing else ''}"

    with st.form(form_key):
        # Date & Time inputs
        date_value = transaction.date.date() if is_editing else datetime.date.today()
        time_value = transaction.date.time() if is_editing else datetime.datetime.now().time()

        selected_date = st.date_input("Select date", value=date_value)
        col1, col2, col3 = st.columns(3)

        with col1:
            hour = st.selectbox("Hour", list(range(1, 13)), index=(time_value.hour % 12) - 1 if is_editing else 0)
        with col2:
            minute = st.selectbox("Minute", list(range(0, 60)), index=time_value.minute if is_editing else 0)
        with col3:
            AM_PM = st.selectbox("AM/PM", ['AM', 'PM'], index=0 if time_value.hour < 12 else 1)

        # Common inputs
        amount = st.number_input("Amount", min_value=0.0, value=float(transaction.amount) if is_editing else 0.0, step=0.01)
        description = st.text_input("Description", value=transaction.description if is_editing else "")

        wallet_name = None
        destination_wallet_name = None

        if type in ['Income', 'Expense']:
            category = st.selectbox("Category", categories, index=categories.index(transaction.category) if is_editing else 0)
            wallet_name = st.selectbox("Wallet", [w.name for w in user.wallets],
                                       index=[w.name for w in user.wallets].index(transaction.wallet.name) if is_editing else 0)
        else:
            category = 'Transfer'
            wallet_name = st.selectbox("From Wallet", [w.name for w in user.wallets],
                                       index=[w.name for w in user.wallets].index(transaction.wallet.name) if is_editing else 0)
            destination_wallet_name = st.selectbox("To Wallet", [w.name for w in user.wallets],
                                                   index=[w.name for w in user.wallets].index(transaction.destination_wallet.name) if is_editing else 0)

        cols = st.columns(2)
        with cols[0]:
            submit = st.form_submit_button("Save" if is_editing else "Submit")
        with cols[1]:
            cancel = st.form_submit_button("Cancel")

    if submit:
        # Combine time into datetime
        hour_24 = hour + 12 if AM_PM == "PM" and hour != 12 else hour if AM_PM == "AM" or hour == 12 else 0
        combined_datetime = datetime.datetime.combine(selected_date, datetime.time(hour_24, minute))

        wallet = next((w for w in user.wallets if w.name == wallet_name), None)
        destination_wallet = next((w for w in user.wallets if w.name == destination_wallet_name), None) if destination_wallet_name else None

        if is_editing:
            edit_transaction(
                transaction.id,
                description,
                Decimal(str(amount)),
                category,
                combined_datetime,
                wallet.id,
                destination_wallet.id  if destination_wallet else None,
            )
            
        else:
            add_transaction(
                user.id,
                wallet.id,
                destination_wallet.id if destination_wallet else None,
                combined_datetime,
                category,
                Decimal(str(amount)),
                description,
                type
            )

        st.session_state.show_new_transaction_form = False
        if is_editing:
            st.session_state[f'show_edit_transaction_form{transaction.id}'] = False
        st.rerun()

    if cancel:
        st.session_state.show_new_transaction_form = False
        if is_editing:
            st.session_state[f'show_edit_transaction_form{transaction.id}'] = False
        st.rerun()

def transactions_tab(user):
    if len(user.wallets)==0:
        st.write("You have no wallet. You must create a wallet before you can add a new transaction.")
    else:
        if 'show_new_transaction_form' not in st.session_state:
            st.session_state.show_new_transaction_form = False

        if 'upload_transactions' not in st.session_state:
            st.session_state.upload_transactions = False
        
        cols = st.columns(2)
        with cols[0]:
            if st.button("New Transaction", key='newTransaction'):
                st.session_state.show_new_transaction_form = True
        with cols[1]:
            if st.button("Upload Transactions", key='uploadTransactions'):
                st.session_state.upload_transactions = True

        if st.session_state.show_new_transaction_form:
            st.markdown("### New Transaction")
            tabs = st.tabs(['Income','Expense','Transfer'])

            with tabs[0]:
                categories = ['Allowance','Award','Bonus','Dividend','Investment',
                              'Lottery','Salary','Tips','Others']
                transactions_form(user,'Income',categories)

            with tabs[1]:
                categories = ['Bills','Clothing','Education','Entertainment','Fitness',
                            'Health','Food','Gifts','Furniture','Pet','Shopping',
                            'Transportation','Travel','Investment','Others','Household']
                transactions_form(user,'Expense',categories)

            with tabs[2]:
                transactions_form(user,'Transfer')
            
        if st.session_state.upload_transactions:
            uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx"])

            if uploaded_file is not None:
                if uploaded_file.type == "text/csv":
                    transactions_df = pd.read_csv(uploaded_file)

                elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
                    transactions_df = pd.read_excel(uploaded_file)

                transactions_df['Date'] = pd.to_datetime(transactions_df['Date'])
                import_transactions(user,transactions_df)
                st.session_state.upload_transactions = False
                st.rerun()
        
        if len(user.transactions)==0:
            st.write("You have no transactions.") 
        else:
            transactions = sorted(user.transactions, key=lambda txn: txn.date, reverse=True)
            if transactions:
                earliest = transactions[-1].date
                latest = transactions[0].date
            else:
                st.warning("No transactions to display.")
                st.stop()

            # Initialize session state
            if "current_month" not in st.session_state:
                st.session_state.current_month = latest.month
            if "current_year" not in st.session_state:
                st.session_state.current_year = latest.year

            # Previous and Next month logic
            col1, col2, col3 = st.columns([1, 3, 1])
            with col1:
                if st.button("Previous"):
                    if st.session_state.current_month == 1:
                        st.session_state.current_month = 12
                        st.session_state.current_year -= 1
                    else:
                        st.session_state.current_month -= 1

            with col3:
                if st.button("Next"):
                    if st.session_state.current_month == 12:
                        st.session_state.current_month = 1
                        st.session_state.current_year += 1
                    else:
                        st.session_state.current_month += 1

            # Filter transactions for current month and year
            current_month = st.session_state.current_month
            current_year = st.session_state.current_year
            filtered_txns = [
                txn for txn in transactions
                if txn.date.month == current_month and txn.date.year == current_year
            ]
            month_name = datetime.date(1900, current_month, 1).strftime('%B')
            with col2:
                st.markdown(f"### Transactions for {month_name} {current_year}")

            if filtered_txns:
                for txn in filtered_txns:
                    with st.expander(f'{txn.date.strftime("%Y-%m-%d - %I:%M %p")} | {txn.description} | ₹ {txn.amount}'):
                        st.write(f"**Category**: {txn.category}")
                        st.write(f"**Amount**: ₹{txn.amount}")
                        st.write(f"**Date**: {txn.date.strftime('%Y-%m-%d - %I:%M %p')}")
                        st.write(f"**Description**: {txn.description}")
                        st.write(f"**Wallet**: {txn.wallet.name}")
                        if txn.type == "Transfer":
                            st.write(f"**Destination Wallet**: {txn.destination_wallet.name}")
                        st.write(f"**Type**: {txn.type}")

                        if f'show_edit_transaction_form{txn.id}' not in st.session_state:
                            st.session_state[f'show_edit_transaction_form{txn.id}'] = False

                        if f'delete_transaction_{txn.id}' not in st.session_state:
                            st.session_state[f'delete_transaction_{txn.id}'] = False

                        cols = st.columns(2)
                        with cols[0]:
                            if st.button("Edit Transaction", key=f'editTransaction{txn.id}'):
                                st.session_state[f'show_edit_transaction_form{txn.id}'] = True
                        with cols[1]:
                            if st.button("Delete Transaction", key=f'deleteTransaction{txn.id}'):
                                st.session_state[f'delete_transaction_{txn.id}'] = True

                        if st.session_state[f'show_edit_transaction_form{txn.id}']:
                            st.markdown("## Edit Transaction")
                            if txn.type == 'Income':
                                categories = ['Allowance','Award','Bonus','Dividend','Investment',
                                'Lottery','Salary','Tips','Others']
                            elif txn.type == 'Expense':
                                categories = ['Bills','Clothing','Education','Entertainment','Fitness',
                            'Health','Food','Gifts','Furniture','Pet','Shopping',
                            'Transportation','Travel','Investment','Others','Household']
                            else:
                                categories = None
                            transactions_form(user, txn.type, categories, transaction=txn,)

                        if st.session_state[f'delete_transaction_{txn.id}']:
                            delete_transaction(txn.id)
                            st.session_state[f'delete_transaction_{txn.id}'] = False
                            st.rerun()
            else:
                st.info("No transactions for this month.")

def statistics_tab(user):
    if len(user.transactions) == 0:
        st.write("You have no transactions.")
    else:
        transactions = sorted(user.transactions, key=lambda txn: txn.date, reverse=True)

        if transactions:
            earliest = transactions[-1].date
            latest = transactions[0].date
        else:
            st.warning("No transactions to display.")
            st.stop()

        # Initialize session state for month and year
        if "statistics_current_month" not in st.session_state:
            st.session_state.statistics_current_month = latest.month
        if "statistics_current_year" not in st.session_state:
            st.session_state.statistics_current_year = latest.year

        # Previous and Next month logic
        col1, col2, col3 = st.columns([1, 3, 1])
        with col1:
            if st.button("Previous",key="statisticsPrevious"):
                if st.session_state.statistics_current_month == 1:
                    st.session_state.statistics_current_month = 12
                    st.session_state.statistics_current_year -= 1
                else:
                    st.session_state.statistics_current_month -= 1

        with col3:
            if st.button("Next",key='statisticsNext'):
                if st.session_state.statistics_current_month == 12:
                    st.session_state.statistics_current_month = 1
                    st.session_state.statistics_current_year += 1
                else:
                    st.session_state.statistics_current_month += 1
        # Filter transactions for current month/year
        current_month = st.session_state.statistics_current_month
        current_year = st.session_state.statistics_current_year
        monthly_txns = [
            txn for txn in transactions
            if txn.date.month == current_month and txn.date.year == current_year
        ]
        month_name = datetime.date(1900, current_month, 1).strftime('%B')
        with col2:
            st.markdown(f"### Transactions for {month_name} {current_year}")

        if not monthly_txns:
            st.info("No transactions for this month.")
        else:
            # Toggle between Expense and Income
            txn_type = st.radio("Select transaction type:", ["Expense", "Income"], horizontal=True)

            # Filter by selected type
            filtered_txns = [txn for txn in monthly_txns if txn.type == txn_type]

            # Calculate category sums
            category_totals = defaultdict(float)
            for txn in filtered_txns:
                category_totals[txn.category] += (float)(txn.amount)

            if not category_totals:
                st.warning(f"No {txn_type.lower()} transactions this month.")
            else:
                # Doughnut chart using Plotly
                fig = go.Figure(data=[go.Pie(
                    labels=list(category_totals.keys()),
                    values=list(category_totals.values()),
                    hole=0.5,
                    textinfo='label+percent',
                    hoverinfo='label+value'
                )])
                st.plotly_chart(fig, use_container_width=True)

                                  
def dashboard_page():
    session = Session()
    user = session.query(User).options(
        joinedload(User.transactions).joinedload(Transaction.wallet),
        joinedload(User.transactions).joinedload(Transaction.destination_wallet),
        joinedload(User.wallets)
        ).filter_by(email=st.session_state.user.email).first()
    session.close()

    if st.sidebar.button("Sign Out", key='signOut'):
        st.session_state.clear()
        st.rerun()

    tabs = st.tabs(['Transactions','Wallets','Statistics'])
    with tabs[0]:
        transactions_tab(user)

    with tabs[1]:
        wallets_tab(user)
    
    with tabs[2]:
        statistics_tab(user)