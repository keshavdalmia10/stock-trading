import requests
from content import Content, ContentType
from message import Message, Role
from ratelimitexception import RateLimitError
from tenacity import (
    retry,
    stop_after_attempt,
    retry_if_exception_type,
    before_sleep_log,
    RetryCallState
)
import logging 
logger = logging.getLogger(__name__)

api_key = "sk-None-V2FETT1uumhVRxsCpPMtT3BlbkFJUtfuuX1ZNMC4fCzqryr8"

headers = {
  "Content-Type": "application/json",
  "Authorization": f"Bearer {api_key}"
}

def check_response(response):
    if response.status_code == 429:
        error_data = response.json().get("error", {})
        retry_after_str = error_data.get("message", "").split("try again in ")[-1].split("s.")[0]
        retry_after = float(retry_after_str) if retry_after_str else 10.0  # Default to 10 seconds if not specified
        logger.info("Rate limit hit")
        raise RateLimitError(f"Rate limit exceeded. Retrying after {retry_after} seconds...", retry_after)
    elif not response.ok:
        response.raise_for_status()

def custom_wait(retry_state: RetryCallState):
    if isinstance(retry_state.outcome.exception(), RateLimitError):
        # Get the retry_after value from the exception
        retry_after = retry_state.outcome.exception().retry_after
        # Calculate the exponential backoff wait time
        exponential_wait = min(60, (2 ** retry_state.attempt_number) + retry_after)
        return exponential_wait
    else:
        return 0  # No wait time for other exceptions
    
@retry(
    stop=stop_after_attempt(10),  # Stop after 5 attempts
    wait=custom_wait,  # Use custom wait function
    retry=retry_if_exception_type(RateLimitError),  # Retry on rate limit errors
    before_sleep=before_sleep_log(logger, logging.INFO)  # Log before sleeping
)
def getResponse(payload):
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    check_response(response)  # Check the response and raise exceptions if needed
    
    response_data = response.json()
    answer = response_data['choices'][0]['message']['content']
    return answer

def convert_airesponse_toMessage(response):
   text_content = Content(content_type=ContentType.TEXT, value = response)
   message = Message(role=Role.SYSTEM, content=[text_content])
   return message