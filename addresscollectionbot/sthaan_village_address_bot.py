
import streamlit as st
import json
from bot_utils import replay_chat
from common import intro_prompt

#Initialize Streamlit session
USER_AVATAR = "👤"
BOT_AVATAR = "🤖"

questions = [
    'Thank you. Now we can move on to collect your address. Can you please provide your House number or name of house or some other identity of the house',
    'Can you please provide the name of the society or road where it is situated?',
    'Can you tell me about any landmarks nearby, so that our delivery agents can find you more easily? Since you are in a village proper landmarks will be a great help.',
    'What is the name of the village?',
    'What is the state?',
    'What is the pincode?',
    'Can you provide any delivery prefrences for example "Leave the package at door or with guard" if any',
    'Can you provide the prefered time slot of your availability to collect the delivery'
    ]

json_formats = [
    'Return JSON with key as "house_identity"',
    'Return JSON with key as "society_or_road"',
    'Return JSON with key as "landmarks" and value should be array containing all the landmarks',
    'Return JSON with key as "village"',
    'Return JSON with key as "state"',
    'Return JSON with key as "pincode"',
    'Return JSON with key as "delivery_preferences"',
    'Return JSON with key as "time_slot"'
    ]

json_keys = [
    'house_identity',
    'society_or_road',
    'landmarks',
    'village',
    'state',
    'pincode',
    'delivery_preferences',
    'time_slot'
    ]


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

def state_village_type():
    name = st.session_state["contact_json"]["name"]
    if "village_state" not in st.session_state:
        # If it doesn't exist, initialize it with a default value
        st.session_state["village_state"] = 0
    # else:
        # st.session_state["village_state"] += 1

    if st.session_state["village_state"] >= len(questions):
        st.session_state['address_state_mc'].run_next("Exit")
        return
    
    #Collecting contact number 
    count = st.session_state["village_state_attempt"]
    #FIXME Add retry support

    #FIXME: Add retry support
    idx = st.session_state["village_state"]

    question = questions[idx]

    bot_question =  (name + ('Sorry I couldnt get that. ' if count > 1 else ', ' ) + question)

    st.session_state['bot_question'].append(bot_question)
    replay_chat()
    st.text_input(label=USER_AVATAR, key=json_keys[idx], on_change=fetch_village_details, args=(question, idx))

def fetch_village_details(*args):
    question = ''
    idx = None
    if any(args): 
        question = args[0]
        idx = args[1]

        if "village_state_attempt" not in st.session_state:
            # If it doesn't exist, initialize it with a default value
            st.session_state["village_state_attempt"] = 0

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
            st.session_state["village_state"] += 1
            st.session_state["village_state_attempt"] = 0
        else:
            st.session_state["village_state_attempt"] += 1
        #     st.session_state["bot_question"].append(f'Sorry I was not able to get the information, I am an AI bot, it will be helpful if you can provide the information in the correct format. {question}')


        # Continue to gather more information
        if idx < len(questions):
            state_village_type()
        else:
            st.session_state['address_state_mc'].run_next("Exit")
