import streamlit as st
from db import user_login, user_register
from utils import check_password

def auth_page():
    with st.container():
        with st.columns([1, 3, 1])[1]:  # center column
            tab1, tab2 = st.tabs(["Login", "Register"])
            
            with tab1:
                with st.form("login_form"):
                    email = st.text_input("Email", key="login_email")
                    password = st.text_input("Password", type="password", key="login_password")
                    login_submit = st.form_submit_button("Login")

                    if login_submit:
                        user = user_login(email)
                        if user is None:
                            st.error("Unregistered email.")
                        elif not check_password(password,user.password):
                            st.error("Incorrect password.")
                        else:
                            st.success("Login successful.")
                            st.session_state.user = user
                            st.rerun()

            with tab2:
                with st.form("register_form"):
                    reg_email = st.text_input("Email", key="register_email")
                    reg_password = st.text_input("Password", type="password", key="register_password")
                    reg_submit = st.form_submit_button("Register")

                    if reg_submit:
                        if user_register(reg_email, reg_password):
                            st.success("Registered successfully! You can now log in.")
                        else:
                            st.warning("User already exists.")
                            
    