import os
import requests
from http import HTTPStatus
from pprint import pprint
from typing import Dict, Optional
from requests import Response
from backend.core.config import settings
from backend.schemas.prediction import TimeCodes
from dotenv import load_dotenv

load_dotenv()

BACKEND_API = f"http://api:{os.environ['API_PORT']}"

REGISTER_ENDPOINT = f"{BACKEND_API}{settings.API_V1_STR}/auth/register"
LOGIN_ENDPOINT = f"{BACKEND_API}{settings.API_V1_STR}/auth/login"
CURRENT_USER_ENDPOINT = f"{BACKEND_API}{settings.API_V1_STR}/users/me"
TIMECODES_ENDPOINT = f"{BACKEND_API}{settings.API_V1_STR}/prediction/timecode"
NEW_VIDEO_ENDPOINT = f"{BACKEND_API}{settings.API_V1_STR}/videos/new"

RQ_JOB_FINISHED_STATUS = "finished"
RQ_JOB_FAILED_STATUS = "failed"


def register_user_via_api(username: str, email: str, password: str) -> Response:
    user_data = {
        "name": username,
        "email": email,
        "is_active": True,
        "is_superuser": False,
        "password": password,
    }
    response = requests.post(REGISTER_ENDPOINT, json=user_data)
    return response


def login_via_api(email: str, password: str) -> Response:
    auth_data = {"username": email, "password": password}
    response = requests.post(LOGIN_ENDPOINT, data=auth_data)
    return response


def get_current_user_data_via_api(access_token: str) -> Response:
    headers = {"Authorization": f"Bearer {access_token}"}
    response: Response = requests.get(CURRENT_USER_ENDPOINT, headers=headers)
    return response


def generate_test_prediction_input() -> Dict:
    prediction_create = {
        "Gender": "Male",
        "Age_at_diagnosis": 15000,
        "Primary_Diagnosis": "Oligodendroglioma, NOS",
        "Race": "white",
        # genes
        "IDH1": "MUTATED",
        "TP53": "MUTATED",
        "ATRX": "MUTATED",
        "PTEN": "MUTATED",
        "EGFR": "MUTATED",
        "CIC": "MUTATED",
        "MUC16": "MUTATED",
        "PIK3CA": "MUTATED",
        "NF1": "MUTATED",
        "PIK3R1": "MUTATED",
        "FUBP1": "MUTATED",
        "RB1": "MUTATED",
        "NOTCH1": "MUTATED",
        "BCOR": "MUTATED",
        "CSMD3": "MUTATED",
        "SMARCA4": "MUTATED",
        "GRIN2A": "MUTATED",
        "IDH2": "MUTATED",
        "FAT4": "MUTATED",
        "PDGFRA": "MUTATED",
    }
    return prediction_create


def init_timecode_predict(video_name: str, token: str) -> Response:
    headers = {"Authorization": f"Bearer {token}"}
    response: Response = requests.post(
        TIMECODES_ENDPOINT, json={"video_name": video_name}, headers=headers
    )
    return response


def wait_untill_prediction_end(prediction_id: int, token: str) -> Response:
    waiting_for_predict: bool = True
    headers = {"Authorization": f"Bearer {token}"}
    while waiting_for_predict:
        response: Response = requests.get(
            f"{TIMECODES_ENDPOINT}/{prediction_id}", headers=headers
        )
        response_data = response.json()
        waiting_for_predict = response_data["rq_status"] not in [
            RQ_JOB_FAILED_STATUS,
            RQ_JOB_FINISHED_STATUS,
        ]
    return response


def get_timecode_prediction(prediction_id: int, token: str) -> TimeCodes:
    response = wait_untill_prediction_end(prediction_id=prediction_id, token=token)
    response_data = response.json()
    return TimeCodes.model_validate(response_data["timecodes"])


def get_name_for_new_video() -> str:
    response: Response = requests.get(NEW_VIDEO_ENDPOINT)
    return response.json()["name"]


if __name__ == "__main__":
    from pprint import pprint
    import pickle

    with open(
        "/home/andrey/AS/ITMO/MLServicesProject/ai_ed_coach/timecodes.dill", "rb"
    ) as f:
        data = pickle.load(f)
    TIMECODES: TimeCodes = TimeCodes.model_validate(data)
    pprint(TIMECODES)
