import openai
import os
import math
from flask import Blueprint, request, jsonify
from extension import db
from create_app import createLimiter, createApp
limiter = createLimiter()
from . import chat_bp


client = openai.OpenAI(
    api_key=os.getenv("openai_api_key"),
    base_url=os.getenv("openai_base_url")
)


@chat_bp.route('/send_log_chat', methods=['POST'])
@limiter.limit("1/minute;20/day")
def get_log_response():
    data = request.get_json()
    engine="gpt-3.5-turbo"
    messages = [{"role": "user", "content": data.get('message')}]
    response = client.chat.completions.create(
                    model=engine,
                    messages=messages,
                    max_tokens=256,
                    logprobs=True,
                    top_logprobs=5,
                    temperature=0
                    # frequency_penalty=0,
                    # presence_penalty=0
                )
    return jsonify({
        "result": [cont.token for cont in response.choices[0].logprobs.content],
        "likely": [math.exp(cont.logprob)**3 for cont in response.choices[0].logprobs.content]
    }), 200
    # return [(cont.token, math.exp(cont.logprob)**3) for cont in response.choices[0].logprobs.content], 200


@chat_bp.route('/test', methods=['POST'])
def test():
    return 5, 200