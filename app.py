import streamlit as st
from db import init_db
from auth import auth_page
from dashboard import dashboard_page

init_db()

if 'user' not in st.session_state or st.session_state.user is  None:
    auth_page()
else:
   dashboard_page()
    


   