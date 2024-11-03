intro_prompt = '''
### ROLE ###
You are given the role of an information collection bot for collecting users address related details.
This bot is designed to collect address and delivery preference information to ensure accurate and timely deliveries.
### INSTRUCTIONS ###
Be crisp in response. ALl JSON keys and values should be in string format.
If you can't retrieve the information or the user hasn't mentioned the information in the response, give the key as "Not Mentioned".
'''

leading_questions = {
        "name" : "Hi, I am Sthaan Bot. Let's start by collecting your contact details. Can you tell me your name?",
        "contact_number" : "Can you please provide your contact number without country code?", 
        "location_type" : "Let's start collecting your address and delivery preference information. Could you please tell me if you live in an apartment, a gated community, a village, or another type of location?"
}

leading_json_formats = {
        "name" : 'Return JSON with key as "name". You must identify which part of the response is the name, if name is not present in the response, return "Not Mentioned" as the key.',
        "contact_number": 'Return JSON with key as "contact_number" and the datatype of key should be string not int.',
        "location_type" : 'Return JSON with key as "location_type" and the datatype of key should be string not int.This is the question asked to user : {question}. This is the response received from user : {text}. ### STRICT INSTRUCTIONS ### You MUST give only one of the following response as value. I want no other word in your response. The options are : "Apartment", "Gated Community", "Village", "Another type of location", "Not able to infer"'
}

instructions = {
    'apartment_address' : {
        "questions" : [
            'Thank you. Now we can move on to collect your address. Can you provide please your apartment number?',
            'Can you please provide the name of the tower or building?',
            'What is the name of the area or locality where it is situated?',
            'Can you tell me about any landmarks nearby, so that our delivery agents can find you more easily?',
            'What is the name of the city or town?',
            'What is the state?',
            'What is the pincode?',
            'Can you provide any delivery prefrences for example "Leave the package at door or with guard" if any?',
            'Can you provide the prefered time slot of your availability to collect the delivery?'
        ],

        "json_formats" : [
            'Return JSON with key as "apartment_number", it should only contain the apartment number and no extra information',
            'Return JSON with key as "building", it should only contain the name of the tower or building and no extra information',
            'Return JSON with key as "area", it should only contain the name of the area or locality and no extra information',
            'Return JSON with key as "landmarks" and value should be array containing all the landmarks, if no landmarks are mentioned return "Not Mentioned"',
            'Return JSON with key as "city", it should only contain the name of the city or town and no extra information',
            'Return JSON with key as "state", it should only contain the name of the state and no extra information',
            'Return JSON with key as "pincode", it should only contain the pincode and no extra information in string format',
            'Return JSON with key as "delivery_preferences", it should only contain the delivery preferences and no extra information',
            'Return JSON with key as "time_slot", it should only contain the time slot and no extra information in string format'
        ],

        "json_keys" : [
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
    },
    'gated_community' : {
            "questions" : [
                'Thank you. Now we can move on to collect your address. Can you please your House number?',
                'Can you please provide the name of the gated community or the society?',
                'What is the name of the area or locality where it is situated?',
                'Can you tell me about any landmarks nearby, so that our delivery agents can find you more easily?',
                'What is the name of the city or town?',
                'What is the state?',
                'What is the pincode?',
                'Can you provide any delivery prefrences for example "Leave the package at door or with guard" if any',
                'Can you provide the prefered time slot of your availability to collect the delivery'
            ],

            "json_formats" : [
                'Return JSON with key as "house_number"',
                'Return JSON with key as "gated_community"',
                'Return JSON with key as "area"',
                'Return JSON with key as "landmarks" and value should be array containing all the landmarks',
                'Return JSON with key as "city"',
                'Return JSON with key as "state"',
                'Return JSON with key as "pincode"',
                'Return JSON with key as "delivery_preferences"',
                'Return JSON with key as "time_slot"'
            ],

            "json_keys" : [
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
    },
    
    'generic_address' : {
        "questions" : [
            'Thank you. Now we can move on to collect your address. Can you please provide your House number? or name of house or some other identity of the house',
            'Can you please provide the name of the society or road?',
            'What is the name of the area or locality where it is situated?',
            'Can you tell me about any landmarks nearby, so that our delivery agents can find you more easily?',
            'What is the name of the city or town?',
            'What is the state?',
            'What is the pincode?',
            'Can you provide any delivery prefrences for example "Leave the package at door or with guard" if any',
            'Can you provide the prefered time slot of your availability to collect the delivery'
        ],

        "json_formats" : [
            'Return JSON with key as "house_number"',
            'Return JSON with key as "society_or_road"',
            'Return JSON with key as "area"',
            'Return JSON with key as "landmarks" and value should be array containing all the landmarks',
            'Return JSON with key as "city"',
            'Return JSON with key as "state"',
            'Return JSON with key as "pincode"',
            'Return JSON with key as "delivery_preferences"',
            'Return JSON with key as "time_slot"'
        ],

        "json_keys" : [
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
    },
    
    'village_address' : {
        "questions" : [
            'Thank you. Now we can move on to collect your address. Can you please provide your House number or name of house or some other identity of the house',
            'Can you please provide the name of the society or road where it is situated?',
            'Can you tell me about any landmarks nearby, so that our delivery agents can find you more easily? Since you are in a village proper landmarks will be a great help.',
            'What is the name of the village?',
            'What is the state?',
            'What is the pincode?',
            'Can you provide any delivery prefrences for example "Leave the package at door or with guard" if any',
            'Can you provide the prefered time slot of your availability to collect the delivery'
        ],

        "json_formats" : [
            'Return JSON with key as "house_identity"',
            'Return JSON with key as "society_or_road"',
            'Return JSON with key as "landmarks" and value should be array containing all the landmarks',
            'Return JSON with key as "village"',
            'Return JSON with key as "state"',
            'Return JSON with key as "pincode"',
            'Return JSON with key as "delivery_preferences"',
            'Return JSON with key as "time_slot"'
        ],

        "json_keys" : [
            'house_identity',
            'society_or_road',
            'landmarks',
            'village',
            'state',
            'pincode',
            'delivery_preferences',
            'time_slot'
        ]
    },
}
