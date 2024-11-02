import unittest
from common import intro_prompt, instructions
from langchain_community.llms import Ollama
import json

def get_prompt(question, response, json_format):
    return intro_prompt + f'''
    This is the question asked to the user: {question}
    This is the response received from user : {response}
    Instruction: {json_format}
    ### STRICT INSTRUCTIONS ###
    You have to extract the information from the user's response according to the question, it is possible that user has not mentioned the required information in his response.
    You MUST give only the JSON as plain text. I DON'T WANY ANY OTHER WORD IN YOUR RESPONSE.
    IF THE USER CROSS QUESTIONS, YOU MUST GIVE "Not Mentioned" as the value.
    '''
class NameTests(unittest.TestCase):

    def test_update(self):
        bot_question = "Hi, I am Sthaan Bot. Let's start by collecting your contact details. Can you tell me your name?"
        json_format = 'Return JSON with key as "name". You must identify which part of the response is the name, if name is not present in the response, return "Not Mentioned" as the value.'

        tests = [

            {
                "name" : "User provides full name",
                "user_response": "My name is Shlok Jain",
                "expected_json": {"name": "Shlok Jain"}
            },

            {
                "name" : "User provides only first name",
                "user_response": "Shlok",
                "expected_json": {"name": "Shlok"}
            },

            {
                "name" : "User does not provide a name",
                "user_response": "I don’t want to share my name.",
                "expected_json": {"name": "Not Mentioned"}
            },

            {
                "name" : "User cross-questions without providing name",
                "user_response": "Why do you need my name?",
                "expected_json": {"name": "Not Mentioned"}
            },

            {
                "name" : "User provides name within additional text",
                "user_response": "Sure, my name is Shlok Jain. Nice to meet you!",
                "expected_json": {"name": "Shlok Jain"}
            },

            {
                "name" : "User provides irrelevant information without a name",
                "user_response": "I am from New York.",
                "expected_json": {"name": "Not Mentioned"}
            },

            {
                "name": "User provides a complex name with special characters",
                "user_response": "O'Connor Jr.",
                "expected_json": {"name": "O'Connor Jr."}
            },
            {
                "name": "User provides name with a title",
                "user_response": "Dr. Smith",
                "expected_json": {"name": "Dr. Smith"}
            },
            {
                "name": "User gives a lengthy name with multiple parts",
                "user_response": "Juan Carlos de la Cruz Fernandez",
                "expected_json": {"name": "Juan Carlos de la Cruz Fernandez"}
            },
            {
                "name": "User gives gibberish or non-name input",
                "user_response": "asdfg12345",
                "expected_json": {"name": "Not Mentioned"}
            },
            {
                "name": "User responds with whitespace only",
                "user_response": "   ",
                "expected_json": {"name": "Not Mentioned"}
            }
        ]

        llm = Ollama(model="llama3", base_url="https://ollama.pplus.ai")

        for test in tests:
            with self.subTest(test=test):

                prompt = get_prompt(bot_question, test["user_response"], json_format)

                response = llm.invoke(prompt)

                json_data = json.loads(response)

                # check if the json is as expected
                self.assertEqual(json_data, test["expected_json"], msg = f"Failed test: {test['name']}")



class ContactNumberTests(unittest.TestCase):

    def test_update(self):
        bot_question = "Can you please provide your contact number without country code?"
        json_format = 'Return JSON with key as "contact_number" and the datatype of key should be string not int.'

        tests = [
            {
                "name": "User provides a valid contact number",
                "user_response": "My number is 1234567890",
                "expected_json": {"contact_number": "1234567890"}
            },
            {
                "name": "User provides contact number with extra characters",
                "user_response": "You can reach me at (987) 654-3210.",
                "expected_json": {"contact_number": "9876543210"}  # Stripped of non-digit characters
            },
            {
                "name": "User provides a number but without enough digits",
                "user_response": "My number is 12345",
                "expected_json": {"contact_number": "Not Mentioned"}
            },
            {
                "name": "User does not provide a number",
                "user_response": "I don’t want to share my number.",
                "expected_json": {"contact_number": "Not Mentioned"}
            },
            {
                "name": "User cross-questions without providing number",
                "user_response": "Why do you need my contact number?",
                "expected_json": {"contact_number": "Not Mentioned"}
            },
            {
                "name": "User provides number amidst other information",
                "user_response": "I'm from gurgaon, and my contact is 9876543210.",
                "expected_json": {"contact_number": "9876543210"}
            },
            {
                "name": "User provides mixed data, number mentioned",
                "user_response": "My old number was 12345, but the new one is 9876543210.",
                "expected_json": {"contact_number": "9876543210"}
            },
            {
                "name": "User provides a non-digit string as contact",
                "user_response": "You can contact me at abcdefg.",
                "expected_json": {"contact_number": "Not Mentioned"}
            },
            {
                "name": "User provides too many digits",
                "user_response": "123456789012345",
                "expected_json": {"contact_number": "Not Mentioned"}
            }
        ]

        llm = Ollama(model="llama3", base_url="https://ollama.pplus.ai")

        for test in tests:
            with self.subTest(test=test):
                prompt = get_prompt(bot_question, test["user_response"], json_format)
                response = llm.invoke(prompt)
                json_data = json.loads(response)
                
                # Check if the JSON is as expected
                self.assertEqual(json_data, test["expected_json"], msg=f"Failed test: {test['name']}")



class LocationTypeTests(unittest.TestCase):

    def test_update(self):
        bot_question = "Let's start collecting your address and delivery preference information. Could you please tell me if you live in an apartment, a gated community, a village, or another type of location?"
        json_format = 'Return JSON with key as "location_type" and the datatype of key should be string not int.This is the question asked to user : {question}. This is the response received from user : {text}. ### STRICT INSTRUCTIONS ### You MUST give only one of the following response as value. I want no other word in your response. The options are : "Apartment", "Gated Community", "Village", "Another type of location", "Not able to infer"'

        tests = [
            {
                "name": "User provides apartment as location",
                "user_response": "I live in an apartment.",
                "expected_json": {"location_type": "Apartment"}
            },
            {
                "name": "User says they live in a gated community",
                "user_response": "I stay in a gated community.",
                "expected_json": {"location_type": "Gated Community"}
            },
            {
                "name": "User lives in a village",
                "user_response": "I'm from a village.",
                "expected_json": {"location_type": "Village"}
            },
            {
                "name": "User provides an unspecified location type",
                "user_response": "I live in a farmhouse.",
                "expected_json": {"location_type": "Another type of location"}
            },
            {
                "name": "User's location type cannot be inferred",
                "user_response": "I'm from a beautiful place.",
                "expected_json": {"location_type": "Not able to infer"}
            },
            {
                "name": "User provides response with extra description",
                "user_response": "I live in a big apartment",
                "expected_json": {"location_type": "Apartment"}
            },
            {
                "name": "User mentions an uncommon type of location",
                "user_response": "I'm in a cabin",
                "expected_json": {"location_type": "Another type of location"}
            },
            {
                "name": "User provides vague response without specifying location type",
                "user_response": "somewhere nice",
                "expected_json": {"location_type": "Not able to infer"}
            },
            {
                "name": "User gives empty response",
                "user_response": "",
                "expected_json": {"location_type": "Not able to infer"}
            }
        ]

        llm = Ollama(model="llama3", base_url="https://ollama.pplus.ai")

        for test in tests:
            with self.subTest(test=test):
                prompt = get_prompt(bot_question, test["user_response"], json_format)
                response = llm.invoke(prompt)
                json_data = json.loads(response)
                
                # Check if the JSON is as expected
                self.assertEqual(json_data, test["expected_json"], msg=f"Failed test: {test['name']}")


if __name__ == '__main__':
    suite = unittest.TestSuite()

    # add all the test classes here!
    suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(NameTests))
    suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(ContactNumberTests))
    suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(LocationTypeTests))
    # suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(<next test class>))
    # ...

    runner = unittest.TextTestRunner()
    runner.run(suite)

