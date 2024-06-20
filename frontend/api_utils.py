import os
import requests
from http import HTTPStatus
from pprint import pprint
from typing import Dict
from requests import Response
from backend.core.config import settings
from dotenv import load_dotenv

load_dotenv()

BACKEND_API = f"http://api:{os.environ['API_PORT']}"

REGISTER_ENDPOINT = f"{BACKEND_API}{settings.API_V1_STR}/auth/register"
LOGIN_ENDPOINT = f"{BACKEND_API}{settings.API_V1_STR}/auth/login"
CURRENT_USER_ENDPOINT = f"{BACKEND_API}{settings.API_V1_STR}/users/me"
PREDS_ENDPOINT = f"{BACKEND_API}{settings.API_V1_STR}/prediction"
USER_PREDS_ENDPOINT = f"{BACKEND_API}{settings.API_V1_STR}/users/me/predictions"
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


def get_current_user_predictions_via_api(access_token: str) -> Response:
    headers = {"Authorization": f"Bearer {access_token}"}
    response: Response = requests.get(USER_PREDS_ENDPOINT, headers=headers)
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


def init_predict(prediction_data: Dict, model_name: str, token: str) -> Response:
    headers = {"Authorization": f"Bearer {token}"}
    response: Response = requests.post(
        f"{PREDS_ENDPOINT}/{model_name}", json=prediction_data, headers=headers
    )
    return response


def wait_untill_prediction_end(prediction_id: int, token: str) -> Response:
    waiting_for_predict: bool = True
    headers = {"Authorization": f"Bearer {token}"}
    while waiting_for_predict:
        response: Response = requests.get(
            f"{PREDS_ENDPOINT}/{prediction_id}", headers=headers
        )
        response_data = response.json()
        waiting_for_predict = response_data["rq_status"] not in [
            RQ_JOB_FAILED_STATUS,
            RQ_JOB_FINISHED_STATUS,
        ]
    return response


def get_name_for_new_video() -> str:
    response: Response = requests.get(NEW_VIDEO_ENDPOINT)
    return response.json()["name"]


if __name__ == "__main__":

    def make_pred():
        token = login_via_api(
            email="shilkov1.one@gmail.com", password="q2w3e4r"
        ).json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        pred_input = generate_test_prediction_input()
        response: Response = requests.post(
            LOGREG_ENDPOINT, json=pred_input, headers=headers
        )
        return response

    def get_pred(id: int):
        token = login_via_api(
            email="shilkov1.one@gmail.com", password="q2w3e4r"
        ).json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        response: Response = requests.get(f"{PREDS_ENDPOINT}/{id}", headers=headers)
        print(response.status_code)
        pprint(response.json())
        # print(response.json()["rq_status"])
        # print(response.json()["result"])

    token = login_via_api(email="shilkov1.one@gmail.com", password="q2w3e4r").json()[
        "access_token"
    ]
    r = get_current_user_predictions_via_api(token)
