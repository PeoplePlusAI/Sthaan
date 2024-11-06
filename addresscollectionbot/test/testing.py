import sys
import os

# Add src directory to the Python path so it can find the my_module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from common import leading_questions as questions
from common import leading_json_formats as json_formats
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
        bot_question = questions['name']
        json_format = json_formats['name']

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
        bot_question = questions['contact_number']
        json_format = json_formats['contact_number']

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
        bot_question = questions['location_type']
        json_format = json_formats['location_type']

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

class ApartmentAddressTests(unittest.TestCase):
    
    def test_apartment_number(self):
        bot_question = instructions['apartment_address']['questions'][0]
        json_format = instructions['apartment_address']['json_formats'][0]
        json_keys = instructions['apartment_address']['json_keys'][0]

        tests = [
            {
                "name": "User provides apartment number",
                "user_response": "My apartment number is 123",
                "expected_json": {json_keys: "123"}
            },
            {
                "name": "User provides apartment number with extra information",
                "user_response": "I live in apartment 123",
                "expected_json": {json_keys: "123"}
            },
            {
                "name": "User provides apartment number with special characters",
                "user_response": "My apartment number is 123A",
                "expected_json": {json_keys: "123A"}
            },
            {
                "name": "User provides apartment number with whitespace",
                "user_response": "  123  ",
                "expected_json": {json_keys: "123"}
            },
            {
                "name": "User does not provide apartment number",
                "user_response": "I don't have an apartment number",
                "expected_json": {json_keys: "Not Mentioned"}
            },
            {
                "name": "User provides apartment number amidst other information",
                "user_response": "I live in apartment 123, in New York",
                "expected_json": {json_keys: "123"}
            },
            {
                "name": "User provides apartment number in a complex response",
                "user_response": "I live in apartment 123. My old apartment number was 456",
                "expected_json": {json_keys: "123"}
            },
            {
                "name": "User provides empty response",
                "user_response": "",
                "expected_json": {json_keys: "Not Mentioned"}
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

    def test_building_name(self):
        bot_question = instructions['apartment_address']['questions'][1]
        json_format = instructions['apartment_address']['json_formats'][1]
        json_keys = instructions['apartment_address']['json_keys'][1]

        tests = [
            {
                "name": "User provides building name",
                "user_response": "I live in the Empire State Building",
                "expected_json": {json_keys: "Empire State Building"}
            },
            {
                "name": "User does not provide building name",
                "user_response": "I don't live in a building",
                "expected_json": {json_keys: "Not Mentioned"}
            },
            {
                "name": "User provides building name amidst other information",
                "user_response": "I live in the Empire State Building, in New York",
                "expected_json": {json_keys: "Empire State Building"}
            },
            {
                "name": "User provides building name in a complex response",
                "user_response": "I live in the Empire State Building. My old building was the Chrysler Building",
                "expected_json": {json_keys: "Empire State Building"}
            },
            {
                "name": "User provides empty response",
                "user_response": "",
                "expected_json": {json_keys: "Not Mentioned"}
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

    def test_area_name(self):
        bot_question = instructions['apartment_address']['questions'][2]
        json_format = instructions['apartment_address']['json_formats'][2]
        json_keys = instructions['apartment_address']['json_keys'][2]

        tests = [
            {
                "name": "User provides area name",
                "user_response": "I live in Gurgaon",
                "expected_json": {json_keys: "Gurgaon"}
            },
            {
                "name": "User does not provide area name",
                "user_response": "I don't live in an area",
                "expected_json": {json_keys: "Not Mentioned"}
            },
            {
                "name": "User provides area name amidst other information",
                "user_response": "I live in Gurgaon, in Haryana",
                "expected_json": {json_keys: "Gurgaon"}
            },
            {
                "name": "User provides area name in a complex response",
                "user_response": "I live in Gurgaon. My old area was Delhi",
                "expected_json": {json_keys: "Gurgaon"}
            },
            {
                "name": "User provides empty response",
                "user_response": "",
                "expected_json": {json_keys: "Not Mentioned"}
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

    def test_landmarks(self):
        bot_question = instructions['apartment_address']['questions'][3]
        json_format = instructions['apartment_address']['json_formats'][3]
        json_keys = instructions['apartment_address']['json_keys'][3]

        tests = [
            {
                "name": "User provides landmarks",
                "user_response": "There's a park nearby, and a school",
                "expected_json": {json_keys: ["park", "school"]}
            },
            {
                "name": "User does not provide landmarks",
                "user_response": "There are no landmarks nearby",
                "expected_json": {json_keys: ["Not Mentioned"]}
            },
            {
                "name": "User provides landmarks amidst other information",
                "user_response": "There's a park nearby, and a school. I live in Gurgaon",
                "expected_json": {json_keys: ["park", "school"]}
            },
            {
                "name": "User provides empty response",
                "user_response": "",
                "expected_json": {json_keys: ["Not Mentioned"]}
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
    suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(ApartmentAddressTests))
    # suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(<next test class>))
    # ...

    runner = unittest.TextTestRunner()
    runner.run(suite)

