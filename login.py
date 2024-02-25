import streamlit as st
import streamlit_authenticator as stauth
# import yaml
import toml
from yaml.loader import SafeLoader
import copy
import ast


def login():

    str_credentials = str(st.secrets['credentials'])
    credentials = ast.literal_eval(str_credentials)
    authenticator = stauth.Authenticate(
        credentials,
        st.secrets['cookie']['name'],
        st.secrets['cookie']['key'],
        st.secrets['cookie']['expiry_days']
    )

    name, authentication_status, username = authenticator.login(location='main', fields={'Login':'Login'})
    st.session_state.username = username
    if authentication_status:
        authenticator.logout('Logout', 'main')
            
    elif authentication_status == False:
        st.write(name, username)
        st.error('Username/password is incorrect')
    elif authentication_status == None:
        st.warning('Please enter your username and password')
        
    return authentication_status, name