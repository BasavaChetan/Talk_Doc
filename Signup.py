import streamlit as st 
import pyodbc
import pandas
import hashlib
import numpy 
import re
import time
import os
from dotenv import load_dotenv

load_dotenv()

# Database Connection
conn = pyodbc.connect(f'DRIVER={{ODBC Driver 18 for SQL Server}};'
                      f'SERVER={os.environ.get("SQL_SERVER")};'
                      f'DATABASE={os.environ.get("DATABASE_NAME")};'
                      f'UID={os.environ.get("UID")};'
                      f'PWD={os.environ.get("DATABASE_PWD")};')

cursor = conn.cursor()

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password,hashed_text):
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False

#DB Functions 

def create_usertable():
    cursor.execute('CREATE TABLE IF NOT EXISTS User_Detail(Email,Username,PasswordHash,CreatedDate,LastLogin,IsActive)')


def add_userdata(email,username,password):
      
    cursor.execute('INSERT INTO User_Detail(Email,Username,PasswordHash) VALUES (?,?,?)',(email,username,password))
    conn.commit()
    
	

def login_user(email,password):
    cursor.execute('SELECT * FROM User_Detail WHERE Email =? AND PasswordHash = ?',(email,password))
    
    data =  cursor.fetchall()
    return data


def view_all_users():
    cursor.execute('SELECT * FROM userstable')
    data = cursor.fetchall()
    return data

def is_valid_email(email):
    pattern = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    return pattern.match(email)



def show_login():
    # st.title('Talk_Doc')
    # st.set_page_config(page_title="Login", page_icon=":books:")
    st.markdown("<h1 style='color: black;'>Talk_Doc</h1>", unsafe_allow_html=True)

    st.markdown("""
    <style>
        .block-container {
            background: linear-gradient(135deg, #a1c4fd, #c2e9fb);
            padding: 50px;
            border-radius: 10px;
            box-shadow: 5px 5px 10px gray;
        }
        input, select, button {
            border-radius: 5px !important;
        }
        /* Adding this to center the buttons */
        .stButton>button {
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 0 auto;
        }
        /* Centering the text elements */
        div[data-baseweb="block"] > div > div:only-child {
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)
    
    hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
    st.markdown(hide_st_style, unsafe_allow_html=True)


    if "mode" not in st.session_state:
        st.session_state.mode = "Login"



    with st.container():
        if st.session_state.mode == "Login":
            st.markdown("#### Login")
            with st.form(key='login_form'):
                email = st.text_input("EmailID", key='login_username')
                password = st.text_input("Password", type="password", key='login_password')
                login_button = st.form_submit_button("Login")

                if login_button:
                    hash_pwd = make_hashes(password)
                    result = login_user(email, check_hashes(password, hash_pwd))
                    if result:
                        st.success("Login successful")
                        time.sleep(1)
                        return 1
                    else:
                        st.error("Login failed")
                        return 0
            # st.write("Not a Member?")
            st.markdown("<div style='text-align: center'>Not a Member?</div>", unsafe_allow_html=True)

            if st.button("Sign Up", key="to_signup"):
                st.session_state.mode = "Sign Up"
                st.rerun()

        elif st.session_state.mode == "Sign Up":
            st.markdown("#### Sign Up")
            with st.form(key='signup_form'):
                new_email = st.text_input("Email", key='signup_email')
                new_username = st.text_input("Username", key='signup_username')
                new_password = st.text_input("Password", type="password", key='signup_password')
                signup_button = st.form_submit_button("Sign Up")

                if signup_button:
                    if not new_email:
                        st.error("Email cannot be empty.")
                    elif not is_valid_email(new_email):
                        st.error("Enter a valid email address.")
                    else:
                        cursor.execute('SELECT * FROM User_Detail WHERE Email=?', (new_email,))
                        check_existing_user = cursor.fetchone()
                        if check_existing_user:
                            st.error('Email already exists. Please choose a different one.')
                        else:   
                            add_userdata(new_email, new_username, make_hashes(new_password))
                            st.success("Account created successfully! , Please Login")

            # st.write("Already a Member?")
            st.markdown("<div style='text-align: center'>Already a Member?</div>", unsafe_allow_html=True)
            if st.button("Login", key="to_login"):
                st.session_state.mode = "Login"
                st.rerun()
        


