import streamlit as st
import requests
import json
from langchain_community.llms import Ollama
import json
import re
import ast
llm = Ollama(model="llama3")
import streamlit as st
import json
import ast
import time

def isPhoneValid(s):
    if len(s)!=10:
      return False
    Pattern = re.compile("[6-9][0-9]{9}")
    return Pattern.match(s)
def validatePinCode(s):
    regexm = r"^[1-9][0-9]{5}$"
    return bool(re.match(regexm, s))

intro_prompt = '''
### ROLE ###
You are given the role of an information collection bot for collecting users address related details.
This bot is designed to collect address and delivery preference information to ensure accurate and timely deliveries.
### INSTRUCTIONS ###
Be crisp in response.
'''

# Your existing data
questions = [
    '''Hi, I am Sthaan Bot. Let's start by collecting your contact details. Can you tell me your name?''',
    '''Thank you. Can you please provide your contact number without country code?''',
]
json_format = [
    'Return JSON with key as "name". You must identify which part of the response is the name, YOU MUST NOT RETURN THINGS LIKE {"name":"my name is"} or {"name":"is"} if you cant retrieve name then just return "Not Mentioned"',
    'Return JSON with key as "contact_number" and the datatype of key should be string not int.',
]
json_keys = [
    'name',
    'contact_number',
]

# Initialize session state
if 'question_index' not in st.session_state:
    st.session_state.question_index = 0
if 'contact_json' not in st.session_state:
    st.session_state.contact_json = {}
if 'retry_count' not in st.session_state:
    st.session_state.retry_count = 0
if 'verification_done' not in st.session_state:
    st.session_state.verification_done = False
if 'update_index' not in st.session_state:
    st.session_state.update_index = None
if 'address_verification' not in st.session_state:
    st.session_state.address_verification = False
if 'contact_verification_asked' not in st.session_state:
    st.session_state.contact_verification_asked = False

# Collecting contact information
if st.session_state.question_index < len(questions):
    current_index = st.session_state.question_index
    current_question = questions[current_index]
    st.write(f'Bot: {("Sorry I couldnt get that. " if st.session_state.retry_count > 0 else "") + current_question}')

    user_response = st.text_input("User: ")

    if st.button("Submit"):
        prompt = intro_prompt+ f'''
        This is the question asked to the user: {current_question}
        This is the response received from user : {user_response}
        Instruction: {json_format[current_index]}
        ### STRICT INSTRUCTIONS ###
        You have to extract the information from the user's response according to the question, it is possible that user has not mentioned the required information in his response.
        You MUST give only the JSON as plain text. I DON'T WANT ANY OTHER WORD IN YOUR RESPONSE. Don't change the spelling of words used.
        IF YOU CAN'T RETRIEVE THE INFORMATION OR THE USER HASN'T MENTIONED THE INFORMATION IN THE RESPONSE, GIVE THE KEY AS "Not Mentioned". REMEMBER THIS POINT THIS IS VERY IMPORTANT, WE DON'T WANT WRONG INFORMATION IN OUR DATABASE, MAKE SURE TO RESPOND 'Not Mentioned' IF YOU CAN'T RETRIEVE THE INFORMATION PROPERLY.
        '''
        response = llm.invoke(prompt)
        json_data = json.loads(response)

        st.session_state.contact_json[json_keys[current_index]] = "Not Mentioned"

        if json_keys[current_index] == 'contact_number':
            if not isPhoneValid(json_data[json_keys[current_index]]):
                st.session_state.retry_count += 1
                st.rerun()

        if json_data[json_keys[current_index]] != 'Not Mentioned':
            st.session_state.contact_json[json_keys[current_index]] = json_data[json_keys[current_index]]
            st.session_state.question_index += 1
            st.session_state.retry_count = 0
            st.rerun()

# Verification step
if st.session_state.question_index >= len(questions) and not st.session_state.contact_verification_asked:
    contact_update_question = (
        'Bot: This is the information you provided, I will repeat them just for verification purposes. '
        'If you want to update anything, please let me know. '
        f'The name you provided is {st.session_state.contact_json["name"]} and the contact number is {st.session_state.contact_json["contact_number"]}. '
        'If you want to change anything, please let me know which data you want to update.'
    )
    st.write(contact_update_question)

    contact_update_response = st.text_input("User: ")

    if st.button("Verify"):
        contact_update_prompt = intro_prompt+f'''
        This is the question asked to user: {contact_update_question}
        The response from user: {contact_update_response}
        This is the information in JSON format: {st.session_state.contact_json}
        ###INSTRUCTIONS###
        You have to look at user's response and determine if they want to update any information.
        If they don't want to update anything RETURN "NO" as your response, REMEMBER ONLY "NO", I WANT NO OTHER WORD IN YOUR RESPONSE.
        If they want to update anything, return a text in format of PYTHON LIST containing all the fields that need to be updated.
        For example, if the user wants to update their name and contact number then return ["name", "contact_number"],
        else if the user wants to update their name only then return ["name"]. NO OTHER WORD OR SENTENCE SHOULD BE THERE IN YOUR RESPONSE OTHER THAN THIS PYTHON LIST.
        '''
        response = llm.invoke(contact_update_prompt).strip()
        st.session_state.contact_verification_asked = True
        if response == "NO":
            st.session_state.verification_done = True
            st.session_state.update_index = 0
            st.session_state.update_list = []
            st.rerun()
        else:
            try:
                update_list = ast.literal_eval(response)
                st.session_state.update_index = 0
                st.session_state.update_list = update_list
                st.rerun()
            except:
                st.error("Invalid response from model.")
                st.rerun()

# Handle contact updates
if st.session_state.contact_verification_asked and st.session_state.update_index<len(st.session_state.update_list):
    i = st.session_state.update_list[st.session_state.update_index]
    question = f'I heard you want to update your {i}. Please provide the updated {i}.'
    st.write(question)

    update_response = st.text_input("Update info: ")

    if st.button("Update"):
        prompt = intro_prompt+f'''
        The user had previously given this information: {st.session_state.contact_json[i]}
        But now they want to update: {i}
        The question asked: {question}
        The response from user: {update_response}
        ### STRICT INSTRUCTIONS ###
        You have to extract the updated information from the response, and return it in the form of JSON exactly as it was before.
        You MUST give only the JSON as plain text. I DON'T WANT ANY OTHER WORD IN YOUR RESPONSE. Don't change the spelling of words used.
        '''
        response = llm.invoke(prompt)
        json_data = json.loads(response)
        st.session_state.contact_json[i] = json_data[i]

        # Reset the update index and finish verification
        st.session_state.update_index += 1
        if st.session_state.update_index == len(st.session_state.update_list):
            st.session_state.verification_done = True
        st.rerun()

# address information:
def extract_location_type(text):
  question = '''Hi, I am Sthaan Bot. Let's start by collecting your address and delivery preference information. Could you please tell me if you live in an apartment, a gated community, a village, or another type of location?'''
  prompt = intro_prompt+f'''
  This is the question asked to user : {question}
  This is the response received from user : {text}

  ### STRICT INSTRUCTIONS ###
  You MUST give only one of the following response as plain text. I want no other word in your response.
  The options are :
  Apartment
  Gated Community
  Village
  Another type of location
  Not able to infer
  '''
  response = llm.invoke(intro_prompt + prompt)
  # print(response)
  return response

if 'location_type' not in st.session_state:
    st.session_state.location_type = None
if 'json_info' not in st.session_state:
    st.session_state.json_info = {}
if 'collection_done' not in st.session_state:
    st.session_state.collection_done = False
if 'address_verification_asked' not in st.session_state:
    st.session_state.address_verification_asked = False

if st.session_state.location_type is None and st.session_state.verification_done: 
    st.write("Bot: " + "Let's collect your address and delivery preference information. Could you please tell me if you live in an apartment, a gated community, a village, or another type of location?")
    location_type = st.text_input("User: ")
    if st.button("Submit"):
        st.session_state.location_type = extract_location_type(location_type)
        st.session_state.json_info['location_type'] = st.session_state.location_type
        st.rerun()

if st.session_state.location_type is not None and st.session_state.verification_done:
    if st.session_state.location_type == 'Apartment':
        questions = [
            'Thank you. Now we can move on to collect your address. Can you please your apartment number?',
            'Can you please provide the name of the tower or building?',
            'What is the name of the area or locality where it is situated?',
            'Can you tell me about any landmarks nearby, so that our delivery agents can find you more easily?',
            'What is the name of the city or town?',
            'What is the state?',
            'What is the pincode?',
            'Can you provide any delivery prefrences for example "Leave the package at door or with guard" if any?',
            'Can you provide the prefered time slot of your availability to collect the delivery?'
        ]
        json_format = [
            'Return JSON with key as "apartment_number"',
            'Return JSON with key as "building"',
            'Return JSON with key as "area"',
            'Return JSON with key as "landmarks" and value should be array containing all the landmarks',
            'Return JSON with key as "city"',
            'Return JSON with key as "state"',
            'Return JSON with key as "pincode" and the datatype of key should be string not int.',
            'Return JSON with key as "delivery_preferences"',
            'Return JSON with key as "time_slot"'
        ]
        json_keys = [
            'apartment_number',
            'building',
            'area',
            'landmarks',
            'city',
            'state',
            'pincode',
            'delivery_preferences',
            'time_slot'
        ]
    elif st.session_state.location_type == 'Gated Community':
        questions = [
            'Thank you. Now we can move on to collect your address. Can you please your House number?',
            'Can you please provide the name of the gated community or the society?',
            'What is the name of the area or locality where it is situated?',
            'Can you tell me about any landmarks nearby, so that our delivery agents can find you more easily?',
            'What is the name of the city or town?',
            'What is the state?',
            'What is the pincode?',
            'Can you provide any delivery prefrences for example "Leave the package at door or with guard" if any',
            'Can you provide the prefered time slot of your availability to collect the delivery'
        ]
        json_format = [
            'Return JSON with key as "house_number"',
            'Return JSON with key as "gated_community"',
            'Return JSON with key as "area"',
            'Return JSON with key as "landmarks" and value should be array containing all the landmarks',
            'Return JSON with key as "city"',
            'Return JSON with key as "state"',
            'Return JSON with key as "pincode" and the datatype of key should be string not int.',
            'Return JSON with key as "delivery_preferences"',
            'Return JSON with key as "time_slot"'
        ]
        json_keys = [
            'house_number',
            'gated_community',
            'area',
            'landmarks',
            'city',
            'state',
            'pincode',
            'delivery_preferences',
            'time_slot'
        ]
    elif st.session_state.location_type == 'Village':
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
        json_format = [
            'Return JSON with key as "house_identity"',
            'Return JSON with key as "society_or_road"',
            'Return JSON with key as "landmarks" and value should be array containing all the landmarks',
            'Return JSON with key as "village"',
            'Return JSON with key as "state"',
            'Return JSON with key as "pincode" and the datatype of key should be string not int.',
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
    elif st.session_state.location_type == 'Another type of location':
        questions = [
            'Thank you. Now we can move on to collect your address. Can you please provide your House number? or name of house or some other identity of the house',
            'Can you please provide the name of the society or road?',
            'What is the name of the area or locality where it is situated?',
            'Can you tell me about any landmarks nearby, so that our delivery agents can find you more easily?',
            'What is the name of the city or town?',
            'What is the state?',
            'What is the pincode?',
            'Can you provide any delivery prefrences for example "Leave the package at door or with guard" if any',
            'Can you provide the prefered time slot of your availability to collect the delivery'
        ]
        json_format = [
            'Return JSON with key as "house_number"',
            'Return JSON with key as "society_or_road"',
            'Return JSON with key as "area"',
            'Return JSON with key as "landmarks" and value should be array containing all the landmarks',
            'Return JSON with key as "city"',
            'Return JSON with key as "state"',
            'Return JSON with key as "pincode" and the datatype of key should be string not int.',
            'Return JSON with key as "delivery_preferences"',
            'Return JSON with key as "time_slot"'
        ]
        json_keys = [
            'house_number',
            'society_or_road',
            'area',
            'landmarks',
            'city',
            'state',
            'pincode',
            'delivery_preferences',
            'time_slot'
        ]

    if 'address_index' not in st.session_state:
        st.session_state.address_index = 0
    
    if st.session_state.address_index < len(questions):
        current_index = st.session_state.address_index
        current_question = questions[current_index]
        st.write(f'Bot: {("Sorry I couldnt get that. " if st.session_state.retry_count > 0 else "") + current_question}')

        user_response = st.text_input("User: ")

        if st.button("Submit"):
            prompt = intro_prompt+f'''
            This is the question asked to the user: {current_question}
            This is the response received from user : {user_response}
            Instruction: {json_format[current_index]}
            ### STRICT INSTRUCTIONS ###
            You have to extract the information from the user's response according to the question, it is possible that user has not mentioned the required information in his response.
            You MUST give only the JSON as plain text. I DON'T WANT ANY OTHER WORD IN YOUR RESPONSE. Don't change the spelling of words used.
            IF YOU CAN'T RETRIEVE THE INFORMATION OR THE USER HASN'T MENTIONED THE INFORMATION IN THE RESPONSE, GIVE THE KEY AS "Not Mentioned". REMEMBER THIS POINT THIS IS VERY IMPORTANT, WE DON'T WANT WRONG INFORMATION IN OUR DATABASE, MAKE SURE TO RESPOND 'Not Mentioned' IF YOU CAN'T RETRIEVE THE INFORMATION PROPERLY.
            '''
            response = llm.invoke(prompt)
            json_data = json.loads(response)

            st.session_state.json_info[json_keys[current_index]] = "Not Mentioned"

            if json_keys[current_index] == 'pincode':
                if not validatePinCode(json_data[json_keys[current_index]]):
                    st.session_state.retry_count += 1
                    st.rerun()

            if json_data[json_keys[current_index]] != 'Not Mentioned':
                st.session_state.json_info[json_keys[current_index]] = json_data[json_keys[current_index]]
                st.session_state.address_index += 1
                st.session_state.retry_count = 0
                if st.session_state.address_index == len(questions):
                    st.session_state.collection_done = True
                st.rerun()
            
    if 'address_verification' not in st.session_state:
        st.session_state.address_verification = False
    if st.session_state.address_index >= len(questions) and not st.session_state.address_verification and not st.session_state.address_verification_asked:
        address_update_question = (
            'Bot: This is the information you provided, I will repeat them just for verification purposes. '
            'If you want to update anything, please let me know. '
            'If you want to change anything, please let me know which data you want to update.'
        )
        st.write(address_update_question)
        st.json(st.session_state.json_info)

        address_update_response = st.text_input("User: ")

        if st.button("Verify"):
            address_update_prompt = intro_prompt+f'''
            This is the question asked to user: {address_update_question}
            The response from user: {address_update_response}
            This is the information in JSON format: {st.session_state.json_info}
            ###INSTRUCTIONS###
            You have to look at user's response and determine if they want to update any information.
            If they don't want to update anything RETURN "NO" as your response, REMEMBER ONLY "NO", I WANT NO OTHER WORD IN YOUR RESPONSE.
            If they want to update anything, return a text in format of PYTHON LIST containing all the fields that need to be updated.
            For example, if the user wants to update their name and contact number then return ["name", "contact_number"], 
            else if the user wants to update their name only then return ["name"]. NO OTHER WORD OR SENTENCE SHOULD BE THERE IN YOUR RESPONSE OTHER THAN THIS PYTHON LIST.
            '''
            response = llm.invoke(address_update_prompt).strip()
            st.session_state.address_verification_asked = True
            if response == "NO":
                st.session_state.address_verification = True
                st.session_state.address_update_list = []
                st.session_state.address_update_index = 0
                st.rerun()
            else:
                try:
                    update_list = ast.literal_eval(response)
                    st.session_state.address_update_list = update_list
                    # st.write(update_list)
                    st.session_state.address_update_index = 0
                    st.rerun()
                except:
                    st.error("Something went wrong.")
                    st.rerun()
                
if st.session_state.collection_done and st.session_state.address_verification_asked and st.session_state.address_update_index<len(st.session_state.address_update_list):
    i = st.session_state.address_update_list[st.session_state.address_update_index]
    question = f'I heard you want to update your {i}. Please provide the updated {i}.'
    st.write(question)

    update_response = st.text_input("Update info: ")

    if st.button("Update"):
        prompt = intro_prompt+f'''
        The user had previously given this information: {st.session_state.json_info[i]}
        But now they want to update: {i}
        The question asked: {question}
        The response from user: {update_response}
        ### STRICT INSTRUCTIONS ###
        You have to extract the updated information from the response, and return it in the form of JSON exactly as it was before.
        You MUST give only the JSON as plain text. I DON'T WANT ANY OTHER WORD IN YOUR RESPONSE. Don't change the spelling of words used.
        '''
        response = llm.invoke(prompt)
        json_data = json.loads(response)
        st.session_state.json_info[i] = json_data[i]

        # Reset the update index and finish verification
        st.session_state.address_update_index += 1
        if st.session_state.address_update_index == len(st.session_state.address_update_list):
            st.session_state.address_verification = True
        st.rerun()

if st.session_state.address_verification:
    st.session_state.json_info['contact'] = st.session_state.contact_json
    st.write("Bot: Thank you for providing your address and delivery preferences. We have successfully collected all the required information.")
    st.json(st.session_state.json_info)