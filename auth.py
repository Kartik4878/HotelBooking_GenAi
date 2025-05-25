import os
import requests
import base64
from dotenv import load_dotenv
load_dotenv()
def auth(username,password):
    authstring = f"{username}:{password}"
    authstring = base64.b64encode(authstring.encode()).decode()
    """
    Authenticate a user with the provided username and password.

    Args:
        username (str): The username of the user.
        password (str): The password of the user.

    Returns:
        bool: True if authentication is successful, False otherwise.
    """
    url = f"{os.getenv('PEGA_URL')}casetypes"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {authstring}"  # Ensure this is a valid token
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        os.environ["PEGA_KEY"] = authstring
        return True
    else:
        return False
    
# print(auth("kartik","rules"))
