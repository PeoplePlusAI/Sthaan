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

if __name__ == '__main__':
    suite = unittest.TestSuite()

    # add all the test classes here!
    suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(NameTests))
    # suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(<next test class>))
    # suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(<next test class>))
    # ...

    runner = unittest.TextTestRunner()
    runner.run(suite)

