__author__ = "Thiruvambalam Sreenivas, Arush Upadhyaya,..."

import re
import streamlit as st

#Initialize Streamlit session
USER_AVATAR = "👤"
BOT_AVATAR = "🤖"

#Check if number is valid
def isPhoneValid(s):
    # 1) Then contains 6,7 or 8 or 9.
    # 2) Then contains 9 digits
    if len(s)!=10:
      return False
    Pattern = re.compile("[6-9][0-9]{9}")
    return Pattern.match(s)

#Basic check if pincode is valid
def validatePinCode(s):
    regexm = r"^[1-9][0-9]{5}$"
    return bool(re.match(regexm, s))

def replay_chat():
    st.title("💬 Chatbot")
    st.caption("🚀 A Streamlit chatbot powered by Adarsh - Sthaan")
    #Populate current state in UI from session
    if st.session_state['bot_question']:
        #Write full including latest - 
        for i in range(len(st.session_state['bot_question'])):
            with st.chat_message(name="assistant", avatar=BOT_AVATAR):
                st.write(st.session_state['bot_question'][i])
            #First time user_response is empty
            if i < len(st.session_state['user_response']) :
                with st.chat_message(name="user", avatar=USER_AVATAR):
                    st.write(st.session_state['user_response'][i])
