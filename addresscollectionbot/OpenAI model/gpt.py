import streamlit as st
from openai import OpenAI
import os
import requests
import json
from supabase import create_client, Client
import random
import base64

st.title("Sthaan Bot")

# Set OpenAI API key from Streamlit secrets
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
sarvamai_api_key = os.environ["SARVAM_API_KEY"]
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def save_to_supabase(data):

    if "contact" not in data:
        return "Contact number is missing"
    if "name" not in data:
        return "Name is missing"
    
    user_pin = str(random.randint(1000, 9999))
    conversation_id = data["contact"]
    
    # Query the Supabase table to check if the user_pin already exists
    existing_pin = supabase.table("sthaan").select("user_pin").eq("user_pin", user_pin).execute()
    
    # Keep generating new pins until a unique one is found
    while existing_pin.data:  # If data is not empty, the pin exists
        user_pin = str(random.randint(1000, 9999))
        existing_pin = supabase.table("sthaan").select("user_pin").eq("user_pin", user_pin).execute()
    
    # Prepare the data to push to the Supabase table
    to_push = {
        "conversation_id": conversation_id,
        "user_name": data["name"],
        "address_json": data,
        "user_wa_phone_number": data["contact"],
        "user_pin": user_pin,
    }
    #the primary key is conversation_id
    #check if the conversation_id already exists in the table, if yes edit the row, if no insert a new row
    existing_conversation = supabase.table("sthaan").select("conversation_id").eq("conversation_id", conversation_id).execute()
    if existing_conversation.data:
        supabase.table("sthaan").update(to_push).eq("conversation_id", conversation_id).execute()
    else:
        supabase.table("sthaan").insert(to_push).execute()
    return "Data saved successfully"


# def tts(input : str, st):
#     response_data = response.json()
#     audio_data_base64 = response_data['audios'][0]  # The first audio clip
#     audio_data = base64.b64decode(audio_data_base64)
#     st.session_state.audios.append(audio_data)

initial_prompt = '''
###BACKGROUND###
You are an AI powered 'Sthaan' address collection bot. You are collecting address for an initiative named 'Sthaan' which is started by the organization People+AI, it is based in India.
The aim of this initiative is to digitalize the addressing system in India. You have to collect the information from users with utmost accuracy and precision.
You have to collect information form user by asking them questions. You will be given a set of information based on different scenarios of user's address, strictly follow the instructions given to you.
First you have to collect contact information of the user including Contact Number (JSON key 'contact') and Name (JSON key 'name'). Ask for contact number and name in same question.
Then you have to ask them which type of location they live in, giving them 4 options: Apartment, Gated Community, Village, Other. You have to try to match user's response with the given options and if you can't match, go with the option 'Other'. (JSON key: 'location_type')
Now, you have to collect location specific information based on the type of location they live in.

1. Apartment:
Ask for the following:
- Apartment/flat number (compulsory) --> JSON key: "apartment_number"
- Name of the apartment (compulsory) --> JSON key: "apartment_name"
- Street/Area/Locality (compulsory) --> JSON key: "street_area_locality"
- City (compulsory) --> JSON key: "city"
- State (Try to judge from the city, if not successful, ask the user)(compulsory) --> JSON key: "state"
- Pincode (compulsory) --> JSON key: "pincode"
- Landmarks (compulsory) --> JSON key: "landmarks"

2. Gated Community:
Ask for the following:
- House number (compulsory) --> JSON key: "house_number"
- Name of the gated community/Society (compulsory) --> JSON key: "community_name"
- Street/Area/Locality (compulsory) --> JSON key: "street_area_locality"
- City (compulsory) --> JSON key: "city"
- State (Try to judge from the city, if not successful, ask the user)(compulsory) --> JSON key: "state"
- Pincode (compulsory) --> JSON key: "pincode"
- Landmarks (compulsory) --> JSON key: "landmarks"

3. Village:
Ask for the following:
- House number (Optional) --> JSON key: "house_number"
- Name of the village (compulsory) --> JSON key: "village_name"
- Street/Area/Locality (Optional) --> JSON key: "street_area_locality"
- City (compulsary) --> JSON key: "city"
- State (compulsory) --> JSON key: "state"
- Pincode (compulsory) --> JSON key: "pincode"
- Landmarks (Compulsory)(IT IS VERY IMPORTANT TO ASK FOR LANDMARK IN VILLAGE, it will be better if we have more than 2-3 landmarks) --> JSON key: "landmarks"

4. Other:
Ask for the following:
- House/Apartment number (Optional) --> JSON key: "house_apartment_number"
- Street/Area/Locality (compulsory) --> JSON key: "street_area_locality"
- City (compulsory) --> JSON key: "city"
- State (Try to judge from the city, if not successful, ask the user)(compulsory) --> JSON key: "state"
- Pincode (compulsory) --> JSON key: "pincode"
- Landmarks (compulsory) --> JSON key: "landmarks"

Now, you have to collect delivery preferences of the user, and Preferred time slots for delivery.
Delivery preferences examples: Leave at doorstep, Call before delivery, Leave with neighbour, etc. --> JSON key: "delivery_preferences"
Preferred time slots examples: 1pm to 9pm, 10am-3pm etc. --> JSON key: "preferred_time_slot"

##INSTRUCTIONS ON HOW TO COLLECT DATA AND HOW TO HANDLE CLARIFICATIONS##
- Keep your questions crisp and clear, as short as possible.
- First ask for name and contact number.
- The Name shsould make sense, don't consider any random name like abcd etc. as a valid name. It should contain atleast first name and last name.
- The Contact number should be a valid 10 digit number. Tell then to give it without country code
- If user gives number and pincode in words, it's your responsibility to convert it into digits.
- You should ask for address in single question, which should be "Can you please provide your address?". Then try to extract the information listed above from the user's response. If any of the information is missing, ask for the missing information smartly, like for eg. if apartment number is missing, ask for it by saying "I saw your apartment number is missing, Can you please provide your apartment number?".
- Landmarks should be a python list, which should contain all landmarks given by user.
- If user asks for any clarification, you should respond accordingly, and at last of response also add the same question again, so that user can answer it.
- Pincode should be 6 digit number.
- Check for missing information, if any information is missing, ask for the missing information.
- Ask for delivery preferences and preferred time slots.
- Don't answer random questions, only answer the questions related to the information collection. Don't go out of the context.
- Once all the information is collected, provide the information in JSON format, with all keys and values in string format, except the landmarks key, which should be a list of strings.
'''

def extract_info(messages):
    response = messages[-1]["content"]
    try: 
        #consider string starting from { and ending with } as JSON
        res = json.loads(response[response.index("{"):response.rindex("}")+1])
        print(res)
        save_to_supabase(res)
        
    except:
        print(response)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": initial_prompt},
        {"role": "assistant", "content": "Hello! I'm am Sthaan bot, Lets start collecting the address and delivery preference information. Can you please provide your contact number and name?"},
    ]

if "audios" not in st.session_state:
    st.session_state.audios = []

i=0

# if len(st.session_state.messages)==2:
#     tts("Hello! I'm am Sthaan bot, Lets start collecting the address and delivery preference information. Can you please provide your contact number and name?", st)

for message in st.session_state.messages:
    if message["role"] == "system":
        continue
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        # st.session_state.audios[i]
        if i<len(st.session_state.audios) and message["role"]=="assistant":
            st.audio(st.session_state.audios[i])
            i+=1



if "counter" not in st.session_state:
    st.session_state.counter = 0


user_inp = st.audio_input("Audio Input" + str(st.session_state.counter))
if user_inp:
    url = "https://api.sarvam.ai/speech-to-text-translate"
    files = {
        "file": ("file", user_inp, "audio/wav"),
        "prompt": (None, "keep it generous and as it is and translate in english, if user speaks in HINDI."),
        "model": (None, "saaras:v1")
    }

    headers = {
        "api-subscription-key": sarvamai_api_key,
    }

    response = requests.post(url, headers=headers, files=files)

    transcribed_text = response.json()['transcript']
    st.session_state.messages.append({"role": "user", "content": transcribed_text})
    with st.chat_message("user"):
        st.markdown(transcribed_text)
    
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=st.session_state.messages
    )
    response = completion.choices[0].message.content
    # tts(response, st)
    user_inp = None
    st.session_state.counter += 1
    st.session_state.messages.append({"role": "assistant", "content": response})

    extract_info(st.session_state.messages)
    st.rerun()