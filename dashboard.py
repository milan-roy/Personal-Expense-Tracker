import streamlit as st
from sqlalchemy.orm import joinedload
from db import Session,add_wallet, add_transaction
from models import User, Wallet, Transaction
from decimal import Decimal
from streamlit_card import card
import datetime

def wallets_tab(user):
    if len(user.wallets)==0:
            st.text("You have no wallets")
    else:
        sorted_wallets = sorted(user.wallets, key=lambda w: w.id)
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

def transactions_form(user,type,categories=None):
    with st.form(f"add_{type}_form"):
        # Date selection
        selected_date = st.date_input("Select date", value=datetime.date.today())

        # Time selection
        col1, col2, col3 = st.columns(3)
        with col1:
            hour = st.selectbox("Hour", list(range(1, 13)), format_func=lambda x: f"{x:02d}")  # 1-12
        with col2:
            minute = st.selectbox("Minute", list(range(0, 60)), format_func=lambda x: f"{x:02d}")
        with col3:
            AM_PM = st.selectbox("AM/PM", ['AM', 'PM'])

        amount = st.number_input(label="Amount", min_value=0.00, value=0.00,step=0.01)
        amount = Decimal(str(amount))

        description = st.text_input("Description")
        if type in ['Income','Expense']:
            category = st.selectbox("Category", categories) 
            wallet_name = st.selectbox("Wallet",[wallet.name for wallet in user.wallets])
        else:
            category = 'Transfer'
            wallet_name = st.selectbox("From Wallet",[wallet.name for wallet in user.wallets])
            destination_wallet_name = st.selectbox("To Wallet",[wallet.name for wallet in user.wallets])
        
        cols = st.columns(2) 
        with cols[0]:
            submit = st.form_submit_button("Submit")
        with cols[1]:
            cancel = st.form_submit_button("Cancel")

    if submit:
        # Convert 12-hour time to 24-hour
        if AM_PM == "PM" and hour != 12:
            hour_24 = hour + 12
        elif AM_PM == "AM" and hour == 12:
            hour_24 = 0
        else:
            hour_24 = hour

        combined_datetime = datetime.datetime.combine(
            selected_date,
            datetime.time(hour_24, minute)
        )
        wallet_id = next((w for w in user.wallets if w.name == wallet_name), None).id
        if type == 'Transfer':
            destination_wallet_id = next((w for w in user.wallets if w.name == destination_wallet_name), None).id
        else:
            destination_wallet_id = None
        add_transaction(user.id, 
                        wallet_id,
                        destination_wallet_id,
                        combined_datetime, 
                        category, 
                        amount, 
                        description,
                        type)
        st.session_state.show_new_transaction_form = False
        st.rerun()
    
    if cancel:
        st.session_state.show_new_transaction_form = False
        st.rerun()

                        
def transactions_tab(user):
    if len(user.wallets)==0:
        st.write("You have no wallet. You must create a wallet before you can add a new transaction.")
    else:
        if len(user.transactions)==0:
            st.write("You have no transactions.") 
    
        if 'show_new_transaction_form' not in st.session_state:
            st.session_state.show_new_transaction_form = False

        if st.button("New Transaction", key='newTransaction'):
            st.session_state.show_new_transaction_form = True

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
                
                
def dashboard_page():
    session = Session()
    user = session.query(User).options(
        joinedload(User.transactions).joinedload(Transaction.wallet),
        joinedload(User.transactions).joinedload(Transaction.destination_wallet),
        joinedload(User.wallets)
        ).filter_by(email=st.session_state.user.email).first()

    if st.sidebar.button("Sign Out", key='signOut'):
        st.session_state.clear()
        st.rerun()

    tabs = st.tabs(['Transactions','Wallets'])
    with tabs[0]:
        transactions_tab(user)

    with tabs[1]:
        wallets_tab(user)