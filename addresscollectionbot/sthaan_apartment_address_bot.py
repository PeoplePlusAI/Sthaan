import streamlit as st
import json
from bot_utils import replay_chat
from common import intro_prompt, instructions

#Initialize Streamlit session
USER_AVATAR = "👤"
BOT_AVATAR = "🤖"

questions = instructions['apartment_address']['questions']
json_formats = instructions['apartment_address']['json_formats']
json_keys = instructions['apartment_address']['json_keys']

def get_prompt(question, response, json_format):
    return intro_prompt + f'''
            This is the question asked to the user: {question + json_format}
            This is the response received from user : {response}
            ### STRICT INSTRUCTIONS ###
            You have to extract the information from the user's response according to the question.
            You have to give the JSON containing the information given by the user.
            You MUST give only the JSON as plain text. I DON'T WANY ANY OTHER WORD IN YOUR RESPONSE. Don't change the spelling of words used.
            If you can't retrieve the information or the user hasn't mentioned the information in the response, give the key as "Not Mentioned", remember this point this is very important, we don't want wrong information in our database, make sure to respond not mentioned if you don't get the information properly.
            '''

def state_apartment_type():
    if "attempt" not in st.session_state:
            # If it doesn't exist, initialize it with a default value
            st.session_state["attempt"] = 0

    name = st.session_state["contact_json"]["name"]
    if "apartment_state" not in st.session_state:
        # If it doesn't exist, initialize it with a default value
        st.session_state["apartment_state"] = 0
    else:
        if st.session_state['attempt']==0:
            st.session_state["apartment_state"] += 1

    if st.session_state["apartment_state"] >= len(questions):
        st.session_state['address_state_mc'].run_next("Exit")
        return
    
    #Collecting contact number 
    count = st.session_state["attempt"]
    
    idx = st.session_state["apartment_state"]

    question = questions[idx]

    bot_question =  (name + ', ' + ('Sorry I couldnt get that. ' if count>=1 else '' ) + question)

    st.session_state['bot_question'].append(bot_question)
    replay_chat()
    st.text_input(label=USER_AVATAR, key=json_keys[idx], on_change=fetch_apartment_details, args=(question, idx))

def fetch_apartment_details(*args):
    question = ''
    idx = None
    if any(args): 
        question = args[0]
        idx = args[1]  

        session_key = json_keys[idx]

        response = st.session_state[session_key]

        st.session_state[session_key] = ''
        st.session_state['user_response'].append(response)

        json_format = json_formats[idx]

        prompt = get_prompt(question, response, json_format)
        #Calling llm to extract location entity in proper json format
        response = st.session_state["llm"].invoke(prompt)

        json_data = json.loads(response)
        st.session_state["contact_json"][json_keys[idx]] = 'Not Mentioned'
        if json_data[json_keys[idx]] != 'Not Mentioned':
            st.session_state["contact_json"][json_keys[idx]] = json_data[json_keys[idx]]
            st.session_state["attempt"] = 0
        else:
            st.session_state["attempt"] += 1
        
        if idx < len(questions):
            state_apartment_type()
        else:
            st.session_state['address_state_mc'].run_next("Exit")
