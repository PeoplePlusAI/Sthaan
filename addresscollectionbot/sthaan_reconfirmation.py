
import streamlit as st
import json
from bot_utils import replay_chat
import ast
from common import intro_prompt

#Initialize Streamlit session
USER_AVATAR = "👤"
BOT_AVATAR = "🤖"

def state_reconfirmation():

    info_json = st.session_state['contact_json']
    address_update_question = 'This is the information you provided, I will repeat them just for verification purposes, if you want to update anything then please let me know. The data you provided is as follows:' + str(info_json) + '. If you want to change anything then please let me know in which data do you want to make changes.'
    bot_question = address_update_question 

    st.session_state['bot_question'].append(bot_question)

    replay_chat()
    st.text_input(label=USER_AVATAR, key="user_reconfirmation", on_change=fetch_reconfirmation, args=(address_update_question, info_json))
    
def fetch_reconfirmation(*args):

    if any(args): 
        address_update_question = args[0]
        info_json = args[1]
    
    address_update_response= st.session_state['user_reconfirmation']
    st.session_state['user_reconfirmation'] = ''

    st.session_state['user_response'].append(address_update_response)
    address_update_question = ''

    address_update_prompt = intro_prompt + f'''
    This is the question asked to user: {address_update_question}
    The response from user: {address_update_response}
    This is the information in JSON format: {info_json}
    ###INSTRUCTIONS###
    You have to look at user's response and determine if they want to update any information.
    If they dont want to update anything RETURN "NO" as your response, REMEMBER ONLY "NO", I WANT NO OTHER WORD IN YOUR RESPONSE.
    If they want to update anything the a text in format of PYTHON LIST containing all the fields that need to be updated. For eg. if user wants to update his area and landmarks then return ["area", "landmarks"], else if user wants to update his pincode only then return ["pincode"]. NO OTHER WORD OR SENTENCE SHOULD BE THERE IN YOUR RESPONSE OTHER THAN THIS PYTHON LIST.
    '''
    #Interpret user intent and respond with list of intent or "No"
    response = st.session_state["llm"].invoke(address_update_prompt)


    if response.strip() != 'NO':
        update_list = ast.literal_eval(response)
        st.session_state['address_updates'] = update_list
        if "address_update_state" not in st.session_state:
            # If it doesn't exist, initialize it with a default value
            st.session_state["address_update_state"] = 0
        else:
            st.session_state["address_update_state"] += 1
        
        state_addr_update()
    else :
        bot_question = f'Saving your information. Goodbye'
        st.session_state['bot_question'].append(bot_question)
        replay_chat()
        os.makedirs("data/", exist_ok=True)
        with open('data/' + st.session_state['contact_json']['contact_number'] + '.json', "w") as file:
            json.dump(st.session_state['contact_json'], file)
        return None

def state_addr_update():
    update_list = st.session_state['address_updates']
    idx = st.session_state["address_update_state"]
    
    if st.session_state["address_update_state"] >= len(st.session_state['address_updates']):
        st.session_state['address_state_mc'].run_next("Exit")
        return
    
    update_request = st.session_state['address_updates'][idx]
    bot_question = f'I heard you want to update your {update_request}. Please provide the updated {update_request}.'
    st.session_state['bot_question'].append(bot_question)

    
    replay_chat()
    st.text_input(label=USER_AVATAR, key=update_request, on_change=fetch_updateadr, args=(update_request, bot_question, idx))

def fetch_updateadr(*args):
    if any(args): 
        key = args[0]
        question = args[1]
        idx = args[2]

    info_json = st.session_state['contact_json']
    response = st.session_state[key]
    st.session_state[key] = ''

    st.session_state['user_response'].append(response)
    address_update_question = ''
        
    prompt = intro_prompt + f'''
    The user had previously given this information: {{'{key}':'{info_json[key]}'}}
    But now he wants to update: {key}
    The question asked: {question}
    The response from user: {response}
    ### STRICT INSTRUCTIONS ###
    You have to extract the upadted information from response, and return it in form of JSON exactly it was before.
    You MUST give only the JSON as plain text. I DON'T WANY ANY OTHER WORD IN YOUR RESPONSE. Don't change the spelling of words used
    '''
    response = st.session_state["llm"].invoke(prompt)
    json_data = json.loads(response)
    st.session_state['contact_json'][key] = json_data[key]

    if idx < len(st.session_state['address_updates']):
        st.session_state["address_update_state"] += 1
        state_addr_update()
    else:
        st.session_state['address_state_mc'].run_next("Exit")

