#   Note 
# # please install below dependencies through terminal 
# pip install --upgrade openai
# pip install requests
# pip install pyaudio
# pip install regex

#Also specify the below keys - 
sarvamai_api_key = ""       # declare keys inside the quotes
openai_api_key = ""



import pyaudio
import wave
import requests
import openai
import json
import base64
import regex as re



def record_stt():
    FORMAT = pyaudio.paInt16  # Format of wave
    CHANNELS = 1  # Number of channels (1 for mono)
    RATE = 16000  # Sample rate (16kHz)
    CHUNK = 1024  # Chunk size
    RECORD_SECONDS = 10  # Duration to record (5 seconds)
    WAVE_OUTPUT_FILENAME = "output.wav"  # Output file name
    # Initialize PyAudio object
    audio = pyaudio.PyAudio()

    # Start recording
    print("Recording...")
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)
    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    # Stop recording
    print("Finished recording.")
    stream.stop_stream()
    stream.close()
    audio.terminate()


    # Save the recorded audio as a WAV file
    wave_file = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wave_file.setnchannels(CHANNELS)
    wave_file.setsampwidth(audio.get_sample_size(FORMAT))
    wave_file.setframerate(RATE)
    wave_file.writeframes(b''.join(frames))
    wave_file.close()


    # Now, send the WAV file to the speech-to-text API (Hindi ASR)
    url = "https://api.sarvam.ai/speech-to-text-translate"

    api_key = sarvamai_api_key                      #Enter your API key

    # Open the recorded WAV file
    with open(WAVE_OUTPUT_FILENAME, 'rb') as audio_file:
        files = {
            'file': (WAVE_OUTPUT_FILENAME, audio_file, 'audio/wav'),
            "prompt": (None, "keep it generous and as it is and translate in english, if user speaks in HINDI."),
            "model": (None, "saaras:v1")
            #'language_code': (None, 'hi-IN')  # 'hi-IN' for Hindi language
        }

        headers = {
            "api-subscription-key": api_key,
        }

        # Send the POST request
        response = requests.post(url, headers=headers, files=files)

        # Get the transcribed text from the response
        transcribed_text = response.json()['transcript']  # Assuming the API returns JSON
        #print("Transcribed Text: ", transcribed_text)

        return transcribed_text

def llm(prompt):
  from openai import OpenAI
   
  client = OpenAI(
    api_key = openai_api_key,
  )

  stream = client.chat.completions.create(
            model = "gpt-4o-mini",
            messages = [{"role": "user", "content": prompt}],
            stream = True,
  )

  response = ""

  for chunk in stream:
      if chunk.choices[0].delta.content is not None:
          response += chunk.choices[0].delta.content

  return response

info_json = {}
contact_json = {}

def extract_location_type(text):
  intro_prompt = '''
  ### ROLE ###
  You are given the role of an information collection bot for collecting users address related details.
  This bot is designed to collect address and delivery preference information to ensure accurate and timely deliveries.
  ### INSTRUCTIONS ###
  Be crisp in response.
  '''
  question = '''Hi, I am Sthaan Bot. Let's start by collecting your address and delivery preference information. Could you please tell me if you live in an apartment, a gated community, a village, or another type of location?'''
  prompt = f'''
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
  response = llm(intro_prompt + prompt)
  # print(response)
  return response

def isPhoneValid(s):
    # 1) Then contains 6,7 or 8 or 9.
    # 2) Then contains 9 digits
    if len(s)!=10:
      return False
    Pattern = re.compile("[6-9][0-9]{9}")
    return Pattern.match(s)

def validatePinCode(s):
    regexm = r"^[1-9][0-9]{5}$"
    return bool(re.match(regexm, s))

def contact():
    intro_prompt = '''
    ### ROLE ###
    You are given the role of an information collection bot for collecting users address related details.
    This bot is designed to collect address and delivery preference information to ensure accurate and timely deliveries.
    ### INSTRUCTIONS ###
    Be crisp in response.
    '''

    
    questions = [
        '''Hi, I am Sthaan Bot. Let's start by collecting your contact details. Can you tell me your name?''',
        '''Thank you. Can you please provide your contact number without country code?''',
    ]
    json_format = [
        'Return JSON with key as "name". You must identify which part of the response is the name, YOU MUST NOT RETURN THINGS LIKE {"name":"my name is"} or {"name":"is"} if you cant retrive name then just return "Not Mentioned"',
        'Return JSON with key as "contact_number" and the datatype of key should be string not int.',
    ]
    json_keys = [
        'name',
        'contact_number',
    ]

    for i, question in enumerate(questions):
        count = 0
        while True:
          count+=1
          print('Bot: ' + ('Sorry I couldnt get that. ' if count>1 else '' ) + question, end='\n')

        # voice responce
          response = record_stt()

        #response = input("User: ")
          prompt = intro_prompt + f'''
          This is the question asked to the user: {question}
          This is the response received from user : {response}
          Instruction: {json_format[i]}
          ### STRICT INSTRUCTIONS ###
          You have to extract the information from the user's response according to the question, it is possible that user has not mentioned the required information in his response.
          You MUST give only the JSON as plain text, NO MARKDOWN, ONLY JSON AS PLAIN TEXT. I DON'T WANY ANY OTHER WORD IN YOUR RESPONSE. Don't change the spelling of words used.
          WHEN THE USER PHONE NUMBER IS ASKED, STORE RESPONSE IN DIGITS, NOT IN WORDS.
          IF YOU CAN'T RETRIEVE THE INFORMATION OR THE USER HASN'T MENTIONED THE INFORMATION IN THE RESPONSE, GIVE THE KEY AS "Not Mentioned", REMEMBER THIS POINT THIS IS VERY IMPORTANT, WE DON'T WANT WRONG INFORMATION IN OUR DATABASE, MAKE SURE TO RESPOND 'Not Mentioned' IF YOU CANT RETRIEVE THE INFORMATION PROPERLY.
          '''
          response = llm(prompt)
          print(response)
          json_data = json.loads(response)
          contact_json[json_keys[i]] = 'Not Mentioned'
          if json_keys[i]=='contact_number':
            if not isPhoneValid(json_data[json_keys[i]]):
                continue
          if json_data[json_keys[i]] != 'Not Mentioned':
            contact_json[json_keys[i]] = json_data[json_keys[i]]
            break

    contact_update_question = 'Bot: This is the information you provided, I will repeat them just for verification purposes, if you want to update anything then please let me know. The name you provided is ' + contact_json['name'] + ' and the contact number is ' + contact_json['contact_number'] + '. If you want to change anything then please let me know in which data do you want to make changes.'
    print(contact_update_question, end='\n')

    #voice response
    contact_update_response = record_stt()

    #contact_update_response = input("User: ")
    contact_update_prompt = intro_prompt + f'''
    This is the question asked to user: {contact_update_question}
    The response from user: {contact_update_response}
    This is the information in JSON format: {contact_json}
    ###INSTRUCTIONS###
    You have to look at user's response and determine if they want to update any information.
    If they dont want to update anything RETURN "NO" as your response, REMEMBER ONLY "NO", I WANT NO OTHER WORD IN YOUR RESPONSE.
    If they want to update anything the a text in format of PYTHON LIST containing all the fields that need to be updated. For eg. if user wants to update his name and contact number then return ["name", "contact_number"], else if user wants to update his name only then return ["name"]. NO OTHER WORD OR SENTENCE SHOULD BE THERE IN YOUR RESPONSE OTHER THAN THIS PYTHON LIST.
    '''
    response = llm(contact_update_prompt)
    print(response)
    if response.strip() != 'NO':
        try:
            update_list = ast.literal_eval(response)
            for i in update_list:
                question = f'I heard you want to update your {i}. Please provide the updated {i}.'
                print(question, end='\n')

            # voice response

                response = record_stt()

                prompt = intro_prompt + f'''
                The user had previously given this information: {{'{i}':'{contact_json[i]}'}}
                But now he wants to update: {i}
                The question asked: {question}
                The response from user: {response}
                ### STRICT INSTRUCTIONS ###
                You have to extract the upadted information from response, and return it in form of JSON exactly it was before.
                You MUST give only the JSON as plain text, NO MARKDOWN, ONLY JSON AS PLAIN TEXT. I DON'T WANY ANY OTHER WORD IN YOUR RESPONSE. Don't change the spelling of words used
                '''
                response = llm(prompt)
                # print(response)
                json_data = json.loads(response)
                contact_json[i] = json_data[i]

        except:
            pass


    print('Bot: Thank you for providing the contact information.', end='\n')
    print(contact_json, end='\n')

def location():
    
    intro_prompt = '''
    ### ROLE ###
    You are given the role of an information collection bot for collecting users address related details.
    This bot is designed to collect address and delivery preference information to ensure accurate and timely deliveries.
    ### INSTRUCTIONS ###
    Be crisp in response.
    '''
    
    question = '''Bot: Could you please tell me if you live in an apartment, a gated community, a village, or another type of location?'''
    print(question, end='\n')

    #voice response
    response = record_stt()

    #response = input("User: ")
    loc_type = extract_location_type(response)
    info_json['location_type'] = loc_type

    if loc_type.strip() == 'Apartment':
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
            'Return JSON with key as "pincode"',
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

      for i, question in enumerate(questions):
            count = 0
            while True:
                count+=1
                print('Bot: ' + ('Sorry I couldnt get that. ' if count>1 else '' ) + question, end='\n')

            #voice response
                response = record_stt()

        #response = input("User: ", end='\n')
                prompt = intro_prompt + f'''
                This is the question asked to the user: {question + json_format[i]}
                This is the response received from user : {response}
                ### STRICT INSTRUCTIONS ###
                You have to extract the information from the user's response according to the question.
                You have to give the JSON containing the information given by the user.
                You MUST give only the JSON as plain text, NO MARKDOWN, ONLY JSON AS PLAIN TEXT. I DON'T WANY ANY OTHER WORD IN YOUR RESPONSE. Don't change the spelling of words used.
                If you can't retrieve the information or the user hasn't mentioned the information in the response, give the key as "Not Mentioned", remember this point this is very important, we don't want wrong information in our database, make sure to respond not mentioned if you don't get the information properly.
                '''
                response = llm(prompt)
                print(response)

                json_data = json.loads(response)
                info_json[json_keys[i]] = 'Not Mentioned'
                if json_data[json_keys[i]] != 'Not Mentioned':
                    info_json[json_keys[i]] = json_data[json_keys[i]]
                    break

    elif loc_type.strip() == 'Gated Community':
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
            'Return JSON with key as "pincode"',
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

      for i, question in enumerate(questions):
            count = 0
            while True:
              count+=1
              print('Bot: ' + ('Sorry I couldnt get that. ' if count>1 else '' ) + question, end='\n')
            #voice response
              response = record_stt()

            #response = input("User: ")
              prompt = intro_prompt + f'''
              This is the question asked to the user: {question + json_format[i]}
              This is the response received from user : {response}
              ### STRICT INSTRUCTIONS ###
              You have to extract the information from the user's response according to the question.
              You have to give the JSON containing the information given by the user.
              You MUST give only the JSON as plain text, NO MARKDOWN, ONLY JSON AS PLAIN TEXT. I DON'T WANY ANY OTHER WORD IN YOUR RESPONSE. Don't change the spelling of words used.
              If you can't retrieve the information or the user hasn't mentioned the information in the response, give the key as "Not Mentioned", remember this point this is very important, we don't want wrong information in our database, make sure to respond not mentioned if you don't get the information properly.
              '''
              response = llm(prompt)
              print(response,end='\n')

              json_data = json.loads(response)
              info_json[json_keys[i]] = 'Not Mentioned'
              if json_data[json_keys[i]] != 'Not Mentioned':
                  info_json[json_keys[i]] = json_data[json_keys[i]]
                  break



    elif loc_type.strip() == 'Village':
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

      for i, question in enumerate(questions):
            count = 0
            while True:
              count+=1
              print('Bot: ' + ('Sorry I couldnt get that. Please remember that I am an AI bot, it will be helpful for me if you answer the question as short as possible' if count>1 else '' ) + question, end='\n')

            #voice response
              response = record_stt()

            #response = input("User: ")
              prompt = intro_prompt + f'''
              This is the question asked to the user: {question + json_format[i]}
              This is the response received from user : {response}
              ### STRICT INSTRUCTIONS ###
              You have to extract the information from the user's response according to the question.
              You have to give the JSON containing the information given by the user.
              You MUST give only the JSON as plain text, NO MARKDOWN, ONLY JSON AS PLAIN TEXT. I DON'T WANY ANY OTHER WORD IN YOUR RESPONSE. Don't change the spelling of words used.
              If you can't retrieve the information or the user hasn't mentioned the information in the response, give the key as "Not Mentioned", remember this point this is very important, we don't want wrong information in our database, make sure to respond not mentioned if you don't get the information properly.
              '''
              response = llm(prompt)
              print(response,end='\n')

              json_data = json.loads(response)
              info_json[json_keys[i]] = 'Not Mentioned'
              if json_data[json_keys[i]] != 'Not Mentioned':
                info_json[json_keys[i]] = json_data[json_keys[i]]
                break


    elif loc_type.strip() == 'Another type of location':
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
            'Return JSON with key as "pincode"',
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

      for i, question in enumerate(questions):
        count = 0
        while True:
          count+=1
          print('Bot: ' + ('Sorry I couldnt get that. ' if count>1 else '' ) + question, end='\n')

            #voice response
          response = record_stt()

            #response = input("User: ")
          prompt = intro_prompt + f'''
          This is the question asked to the user: {question + json_format[i]}
          This is the response received from user : {response}
          ### STRICT INSTRUCTIONS ###
          You have to extract the information from the user's response according to the question.
          You have to give the JSON containing the information given by the user.
          You MUST give only the JSON as plain text, NO MARKDOWN, ONLY JSON AS PLAIN TEXT. I DON'T WANY ANY OTHER WORD IN YOUR RESPONSE. Don't change the spelling of words used.
          If you can't retrieve the information or the user hasn't mentioned the information in the response, give the key as "Not Mentioned", remember this point this is very important, we don't want wrong information in our database, make sure to respond not mentioned if you don't get the information properly.
          '''
          response = llm(prompt)
          print(response,end='\n')

          json_data = json.loads(response)
          info_json[json_keys[i]] = 'Not Mentioned'
          if json_data[json_keys[i]] != 'Not Mentioned':
              info_json[json_keys[i]] = json_data[json_keys[i]]
              break

def address():
    intro_prompt = '''
    ### ROLE ###
    You are given the role of an information collection bot for collecting users address related details.
    This bot is designed to collect address and delivery preference information to ensure accurate and timely deliveries.
    ### INSTRUCTIONS ###
    Be crisp in response.
    '''
    address_update_question = 'Bot: This is the information you provided, I will repeat them just for verification purposes, if you want to update anything then please let me know. The data you provided is as follows:' + str(info_json) + '. If you want to change anything then please let me know in which data do you want to make changes.'
    print(address_update_question, end='\n')

    # voice response
    address_update_response = record_stt()

    #address_update_response = input("User: ")
    address_update_prompt = intro_prompt + f'''
    This is the question asked to user: {address_update_question}
    The response from user: {address_update_response}
    This is the information in JSON format: {info_json}
    ###INSTRUCTIONS###
    You have to look at user's response and determine if they want to update any information.
    If they dont want to update anything RETURN "NO" as your response, REMEMBER ONLY "NO", I WANT NO OTHER WORD IN YOUR RESPONSE.
    If they want to update anything the a text in format of PYTHON LIST containing all the fields that need to be updated. For eg. if user wants to update his area and landmarks then return ["area", "landmarks"], else if user wants to update his pincode only then return ["pincode"]. NO OTHER WORD OR SENTENCE SHOULD BE THERE IN YOUR RESPONSE OTHER THAN THIS PYTHON LIST.
    '''
    response = llm(address_update_prompt)
    print(response)
    if response.strip() != 'NO':
      try:
        update_list = ast.literal_eval(response)
        for i in update_list:
          question = f'I heard you want to update your {i}. Please provide the updated {i}.'
          print(question, end='\n')

          #voice response
          response = record_stt()

          #response = input("User: ")
          prompt = intro_prompt + f'''
          The user had previously given this information: {{'{i}':'{info_json[i]}'}}
          But now he wants to update: {i}
          The question asked: {question}
          The response from user: {response}
          ### STRICT INSTRUCTIONS ###
          You MUST give only the JSON as plain text, NO MARKDOWN, ONLY JSON AS PLAIN TEXT. I DON'T WANY ANY OTHER WORD IN YOUR RESPONSE. Don't change the spelling of words used.
          If you can't retrieve the information or the user hasn't mentioned the information in the response, give the key as "Not Mentioned", remember this point this is very important, we don't want wrong information in our database, make sure to respond not mentioned if you don't get the information properly.
          '''
          response = llm(prompt)
          # print(response)
          json_data = json.loads(response)
          info_json[i] = json_data[i]

      except:
        pass
    print('Bot: Thank you for providing the information.', end='\n')
    print(info_json, end='\n')
    info_json['contact'] = contact_json


#info_json

contact()
location()
address()

info_json = contact_json.update(info_json) 

print(info_json)