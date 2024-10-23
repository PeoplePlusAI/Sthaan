intro_prompt = '''
### ROLE ###
You are given the role of an information collection bot for collecting users address related details.
This bot is designed to collect address and delivery preference information to ensure accurate and timely deliveries.
### INSTRUCTIONS ###
Be crisp in response.
'''

instructions = {
    'apartment_address' : {
        "questions" : [
            'Thank you. Now we can move on to collect your address. Can you please your apartment number?',
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
            'Return JSON with key as "apartment_number"',
            'Return JSON with key as "building"',
            'Return JSON with key as "area"',
            'Return JSON with key as "landmarks" and value should be array containing all the landmarks',
            'Return JSON with key as "city"',
            'Return JSON with key as "state"',
            'Return JSON with key as "pincode"',
            'Return JSON with key as "delivery_preferences"',
            'Return JSON with key as "time_slot"'
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
