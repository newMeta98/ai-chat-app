# backend/utils/helpers.py
from openai import OpenAI
import os

def format_response(data):
    return {"status": "success", "data": data}

def user_message_explanation(message, context, history_explan_mgs):
    api_key = os.getenv('DEEPSEEK_API_KEY')
    model = "deepseek-chat"
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    system_prompt = (
        f"You are an assistant that determines what user said/want's in the user_message, based on conversation context:{context} and previus explaned messages: {history_explan_mgs}  of conversation/user_message."
        "and mainly focusing user_message. Respond with user_message_explanation:[explanation of what user said/want's in the user_message]"
    )
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"user_message:{message}"}
    ]
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages # Adjust based on expected response length
        )
        answer = response.choices[0].message.content
        print(answer)
        return answer
    except Exception as e:
        print(f"Error in can_fast_reply: {e}")
        return False


def user_data_extraction(message, context, user_data):
    
    api_key = os.getenv('DEEPSEEK_API_KEY')
    model = "deepseek-chat"
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    
    system_prompt = (
        "You are a helpful assistant 'Information Extraction Expert'. You will carefuly look at the user_message and extracts from database useful main_Object's that can help in answering user_message.\n" 
        "Determine what main_Object's to extract from database based on user_message, list of main_Object's: personal_information, professional_information, lifestyle, social_interactions, preferences, goals_and_aspirations, conversations_and_interactions\n"
        f"database:{user_data}. Selected main_Object's (can selecte more then one): [main_Object's from list of main_Object's that can contain useful Information]\n"
        "Return user_data:[Extracted Selected main_Object's(all its childerm) from database]\n"
    )
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"user_message:{message}"}
    ]
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages # Adjust based on expected response length
        )
        answer = response.choices[0].message.content
        return answer
    except Exception as e:
        print(f"Error in can_fast_reply: {e}")
        return False

