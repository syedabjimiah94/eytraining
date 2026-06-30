# import random

# def simulate_failure(city: str, data: dict, force: str = None):

#     failure_modes = [
#         "API_DOWN",
#         "SLOW_RESPONSE",
#         "INVALID_RESPONSE",
#         "TIMEOUT",
#         None
#     ]

#     # If force mode is given → override randomness
#     if force == "SUCCESS":
#         return {"status": "SUCCESS", "data": data}

#     if force == "API_DOWN":
#         return {"status": "FAILED", "error": "503 Service Unavailable"}

#     if force == "TIMEOUT":
#         return {"status": "FAILED", "error": "Timeout Error"}

#     if force == "INVALID":
#         return {"status": "FAILED", "error": "Malformed JSON"}

#     # default random behavior
#     failure = random.choice(failure_modes)

#     if failure == "API_DOWN":
#         return {"status": "FAILED", "error": "503 Service Unavailable"}

#     elif failure == "SLOW_RESPONSE":
#         return {"status": "FAILED", "error": "Timeout Error"}

#     elif failure == "INVALID_RESPONSE":
#         return {"status": "FAILED", "error": "Malformed JSON"}

#     elif failure == "TIMEOUT":
#         return {"status": "FAILED", "error": "Request Timeout"}

#     return {"status": "SUCCESS", "data": data}


import time
from langsmith import traceable


# Used only for demo
failure_counter = {
    "TIMEOUT": 0,
    "SLOW_RESPONSE": 0
}

@traceable(name="Failure Simulator")
def simulate_failure(city: str, data: dict, force: str = None):

    global failure_counter

    # -----------------------------
    # NORMAL
    # -----------------------------
    if force is None or force == "NONE":
        return data

    # -----------------------------
    # API DOWN
    # Always Fail
    # -----------------------------
    if force == "API_DOWN":

        return {
            "status": "FAILED",
            "message": "503 Service Unavailable"
        }

    # -----------------------------
    # INVALID RESPONSE
    # Always Fail
    # -----------------------------
    if force == "INVALID_RESPONSE":

        return {
            "status": "FAILED",
            "message": "Invalid API Response"
        }

    # -----------------------------
    # TIMEOUT
    # Fail First Time
    # Success Second Time
    # -----------------------------
    if force == "TIMEOUT":

        if failure_counter["TIMEOUT"] == 0:

            failure_counter["TIMEOUT"] += 1

            return {
                "status": "FAILED",
                "message": "Timeout Error"
            }

        failure_counter["TIMEOUT"] = 0

        return data

    # -----------------------------
    # SLOW RESPONSE
    # Slow First Time
    # Success Second Time
    # -----------------------------
    if force == "SLOW_RESPONSE":

        if failure_counter["SLOW_RESPONSE"] == 0:

            failure_counter["SLOW_RESPONSE"] += 1

            time.sleep(5)

            return {
                "status": "FAILED",
                "message": "Slow Response"
            }

        failure_counter["SLOW_RESPONSE"] = 0

        return data

    return data