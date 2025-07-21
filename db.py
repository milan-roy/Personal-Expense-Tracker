from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
from dotenv import load_dotenv
from models import User, Wallet, Transaction
import os
from utils import hash_password
from sqlalchemy.exc import SQLAlchemyError

# Load variables from .env file into environment
load_dotenv()

# Get the database URL from the environment
DATABASE_URL = os.getenv("DATABASE_URL")

# Create the engine and session factory
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# Create tables, if not already present.
# This will not DROP or clear existing tables.
def init_db():
    Base.metadata.create_all(engine)

def user_register(email,password):
    """
    Check if a user with the same email exists:
        If yes: Return false.
        If no: Create the user in the users table and return true.
    """
    session = Session()
    try:
        if session.query(User).filter_by(email=email).first():
            return False
        user = User(email=email, password=hash_password(password).decode())
        session.add(user)
        session.commit()
        return True
    except SQLAlchemyError as e:
        session.rollback()
        # st.error(f"Error adding user: {e}")
        return False
    finally:
        session.close()

def user_login(email):
    session = Session()
    try:
        user = session.query(User).filter_by(email=email).first()
        return user
    finally:
        session.close()


def add_wallet(user_id, name, amount, type):
    session = Session()
    try:
        wallet = Wallet(user_id=user_id, name=name, amount=amount, type=type)
        session.add(wallet)
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        # st.error(f"Error adding wallet: {e}")
    finally:
        session.close()

def add_transaction(user_id, wallet_id, destination_wallet_id,combined_datetime, 
                    category, amount, description,type):
    session = Session()
    try:
        transaction = Transaction(user_id=user_id, wallet_id = wallet_id, destination_wallet_id = destination_wallet_id,
                    date = combined_datetime,category=category,amount=amount,description=description,type=type)
        wallet = session.query(Wallet).filter_by(id = wallet_id).first()
        if destination_wallet_id:
            destination_wallet = session.query(Wallet).filter_by(id = destination_wallet_id).first()

        if type == 'Expense':
            wallet.amount-=amount
        elif type == 'Income':
            wallet.amount+=amount
        else:
            wallet.amount-=amount
            destination_wallet.amount+=amount

        session.add(transaction)
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
    finally:
        session.close()