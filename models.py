from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

    transactions = relationship("Transaction", back_populates="user")
    wallets = relationship("Wallet", back_populates="user")


class Wallet(Base):
    __tablename__ = 'wallets'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String, nullable=False)
    amount = Column(Numeric, nullable=False)
    type = Column(String, nullable=False)

    user = relationship("User", back_populates="wallets")
    sent_transactions = relationship(
        "Transaction",
        back_populates="wallet",
        foreign_keys="Transaction.wallet_id"
    )
    received_transactions = relationship(
        "Transaction",
        back_populates="destination_wallet",
        foreign_keys="Transaction.destination_wallet_id"
    )

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    wallet_id = Column(Integer, ForeignKey('wallets.id'), nullable=False)  
    destination_wallet_id = Column(Integer, ForeignKey('wallets.id'), nullable=True) 

    date = Column(DateTime, nullable=False)
    category = Column(String, nullable=False)
    amount = Column(Numeric, nullable=False)
    description = Column(String, nullable=True)
    type = Column(String, nullable=False)  

    user = relationship("User", back_populates="transactions")
    wallet = relationship(
        "Wallet",
        back_populates="sent_transactions",
        foreign_keys=[wallet_id]
    )
    destination_wallet = relationship(
        "Wallet",
        back_populates="received_transactions",
        foreign_keys=[destination_wallet_id]
    )
