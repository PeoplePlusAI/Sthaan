__author__ = "Thiruvambalam Sreenivas, Arush Upadhyaya, Slok Jain..."

import streamlit as st
import json
from langchain_community.llms import Ollama
import re
import ast
from common import intro_prompt

from bot_utils import replay_chat, isPhoneValid, validatePinCode  
from sthaan_apartment_address_bot import state_apartment_type
from sthaan_gatedcommunity_address_bot import state_gatedcommunity_type
from sthaan_village_address_bot import state_village_type
from sthaan_generic_address_bot import state_genericadr_type
from sthaan_reconfirmation import state_reconfirmation


#Initialize Streamlit session
USER_AVATAR = "👤"
BOT_AVATAR = "🤖"

#BOT Questions
questions = {
        "name" : "Hi, I am Sthaan Bot. Let's start by collecting your contact details. Can you tell me your name?",
        "contact_number" : "Can you please provide your contact number without country code?", 
        "location_type" : "Let's start collecting your address and delivery preference information. Could you please tell me if you live in an apartment, a gated community, a village, or another type of location?"
}

#Prompt for expected json format
json_formats = {
        "name" : 'Return JSON with key as "name". You must identify which part of the response is the name, YOU MUST NOT RETURN THINGS LIKE {"name":"my name is"} or {"name":"is"} if you cant retrive name then just return "Not Mentioned"',
        "contact_number": 'Return JSON with key as "contact_number" and the datatype of key should be string not int.',
        "location_type" : 'Return JSON with key as "location_type" and the datatype of key should be string not int.This is the question asked to user : {question}. This is the response received from user : {text}. ### STRICT INSTRUCTIONS ### You MUST give only one of the following response as value. I want no other word in your response. The options are : "Apartment", "Gated Community", "Village", "Another type of location", "Not able to infer"'
}

#keys for final output json 
json_keys = [
    'name',
    'contact_number',
    'location_type',
    'apartment_type'
]

def get_prompt(question, response, json_format):
    return intro_prompt + f'''
    This is the question asked to the user: {question}
    This is the response received from user : {response}
    Instruction: {json_format}
    ### STRICT INSTRUCTIONS ###
    You have to extract the information from the user's response according to the question, it is possible that user has not mentioned the required information in his response.
    You MUST give only the JSON as plain text. I DON'T WANY ANY OTHER WORD IN YOUR RESPONSE. Don't change the spelling of words used.
    IF YOU CAN'T RETRIEVE THE INFORMATION OR THE USER HASN'T MENTIONED THE INFORMATION IN THE RESPONSE, GIVE THE KEY AS "Not Mentioned", REMEMBER THIS POINT THIS IS VERY IMPORTANT, WE DON'T WANT WRONG INFORMATION IN OUR DATABASE, MAKE SURE TO RESPOND 'Not Mentioned' IF YOU CANT RETRIEVE THE INFORMATION PROPERLY.
    '''

class StateMachine:
    def __init__(self):
        self.handlers = {}
        self.current_state = None
        self.start_state = None

    def add_state(self, state, handler):
        self.handlers[state] = handler

    def set_start(self, state):
        self.start_state = state
        self.current_state = state

    def run_next(self, current_state):
        try:
            self.current_state = current_state
            handler = self.handlers[current_state]
        except Exception as e:
            print(f"Error: {e}")
            return

        next_state = handler()
        if next_state is not None:
            self.current_state = next_state

#Initialize chatbot and streamlit session 
def init_streamlit_chatbot():


    if 'bot_question' not in st.session_state:
        st.session_state['bot_question'] = []

    if 'user_response' not in st.session_state:
        st.session_state['user_response'] = []

    if 'address_state_mc' not in st.session_state:
        # Core state m/c
        state_machine = StateMachine()

        # State of this address collection
        state_machine.add_state("Start", state_start)
        state_machine.add_state("Name", state_name)
        state_machine.add_state("ContactNumber", state_contact_number)
        state_machine.add_state("LocationType", state_location_type)
        state_machine.add_state("ApartmentAddress", state_apartment_type)
        state_machine.add_state("GatedCommunityAddress", state_gatedcommunity_type)
        state_machine.add_state("VillageAddress", state_village_type)
        state_machine.add_state("GenericAddress", state_genericadr_type)

        #FIXME: Temp comments
        #state_machine.add_state("DeliveryTimePreference", state_delivery_preference)
        #state_machine.add_state("DeliveryInstructions", state_delivery_instructions)
        #state_machine.add_state("Summarize", state_summarize)
        #state_machine.add_state("Update", state_update)
        state_machine.add_state("Exit", state_reconfirmation)

        #Start state
        state_machine.set_start("Start")
        st.session_state['address_state_mc'] = state_machine 
        
        # Initialize UI
        replay_chat()
    
    #Core cotact_json
    if "contact_json" not in st.session_state:
        st.session_state["contact_json"] = {}

    # Initialize an instance of the Ollama model
    if "llm" not in st.session_state:
        st.session_state["llm"] = Ollama(model="llama3", base_url="https://ollama.pplus.ai")
   

    #State M/c Running ----
    if st.session_state['address_state_mc'].current_state == "Start":
        st.session_state['address_state_mc'].run_next("Name")



def state_name():
    # Name and Contact number collection block
    json_key = 'name'
    

    #Collecting name 
    count = 0
    #FIXME Add retry support
    bot_question = (('Sorry I couldnt get that. ' if count>1 else '' ) + questions[json_key])

    with st.chat_message(name="assistant", avatar=BOT_AVATAR):
        st.write(bot_question)

    st.session_state['bot_question'].append(bot_question)

    st.text_input(label=USER_AVATAR, key="user_input_name", on_change=fetch_name)

def fetch_name():
    json_key = 'name'

    response = st.session_state['user_input_name']

    st.session_state['user_input_name'] = ''

    st.session_state['user_response'].append(response)
    
    question = questions[json_key]
    json_format = json_formats[json_key]

    prompt = get_prompt(question, response, json_format)
    #Calling llm to extract location entity in proper json format
    response = st.session_state["llm"].invoke(prompt)

    json_data = json.loads(response)
    st.session_state["contact_json"][json_key] = 'Not Mentioned'
    if json_data[json_key] != 'Not Mentioned':
        st.session_state["contact_json"][json_key] = json_data[json_key]

    #Return next state
    st.session_state['address_state_mc'].run_next("ContactNumber")

def state_contact_number():
    json_key = 'contact_number'
    name = st.session_state["contact_json"]["name"]
    
    #Collecting contact number 
    count = 0
    #FIXME Add retry support
    bot_question =  (name + ('Sorry I couldnt get that. ' if count>1 else ', ' ) + questions[json_key])

    st.session_state['bot_question'].append(bot_question)
   
    replay_chat()
    st.text_input(label=USER_AVATAR, key="user_input_contact", on_change=fetch_contact)

def fetch_contact():
    json_key = 'contact_number'

    response = st.session_state['user_input_contact']

    st.session_state['user_input_contact'] = ''
    st.session_state['user_response'].append(response)

    question = questions[json_key]
    json_format = json_formats[json_key]
   
    prompt = get_prompt(question, response, json_format)
    #Calling llm to extract location entity in proper json format
    response = st.session_state["llm"].invoke(prompt)

    json_data = json.loads(response)
    st.session_state["contact_json"][json_key] = 'Not Mentioned'
    if not isPhoneValid(json_data[json_key]):
        return
    if json_data[json_key] != 'Not Mentioned':
        st.session_state["contact_json"][json_key] = json_data[json_key]
    else:
        st.session_state['bot_question'].append(f'Sorry I was not able to get the information, I am an AI bot, it will be helpful if you can provide the information in the correct format. {question}')
        return

    st.session_state['address_state_mc'].run_next("LocationType")

def state_location_type():
    json_key = 'location_type'
    name = st.session_state["contact_json"]["name"]
    
    #Collecting contact number 
    count = 0
    #FIXME Add retry support
    bot_question =  (name + ('Sorry I couldnt get that. ' if count>1 else ', ' ) + questions[json_key])

    st.session_state['bot_question'].append(bot_question)
   
    replay_chat()
    st.text_input(label=USER_AVATAR, key="user_input_location_type", on_change=fetch_location_type)
    
def fetch_location_type():
    json_key = 'location_type'

    response = st.session_state['user_input_location_type']

    st.session_state['user_input_contact'] = ''
    st.session_state['user_response'].append(response)

    question = questions[json_key]
    json_format = json_formats[json_key]
   
    prompt = get_prompt(question, response, json_format)
    #Calling llm to extract location entity in proper json format
    response = st.session_state["llm"].invoke(prompt)
    json_data = json.loads(response)
    st.session_state["contact_json"][json_key] = 'Not Mentioned'

    if json_data[json_key] != 'Not able to infer':
        location_type = json_data[json_key]
        st.session_state["contact_json"][json_key] = location_type
        # Get Location details based on Location Type
        if location_type == 'Apartment':
            st.session_state['address_state_mc'].run_next("ApartmentAddress")
        elif location_type == 'Gated Community':
            st.session_state['address_state_mc'].run_next("GatedCommunityAddress")
        elif location_type == 'Village':
            st.session_state['address_state_mc'].run_next("VillageAddress")
        elif location_type == 'Another type of location':
            st.session_state['address_state_mc'].run_next("GenericAddress")
    else:
        st.session_state['address_state_mc'].run_next("Exit")

#Start, No ops
def state_start():
    return None

def main():
    #init
    init_streamlit_chatbot()


if __name__ == "__main__":
    main()

