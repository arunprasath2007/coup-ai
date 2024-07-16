import os
import openai

class LLMUtils:
    @staticmethod
    def get_llm_response(system_message: str, user_message: str) -> str:
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            response_format={ "type": "json_object" }
        )
        return response.choices[0].message.content