import streamlit as st
from Signup import show_login
from bot import show_bot


def main():
    
    st.set_page_config(page_title="Talk_Doc", page_icon=":books:")
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        # Show only the login interface
        result = show_login()
        if result:
            st.session_state.logged_in = True
            st.rerun()

    elif st.session_state.logged_in:
        # Show only the bot interface
        show_bot()
        


if __name__ == '__main__':
    main()


