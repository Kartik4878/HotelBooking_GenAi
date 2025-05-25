import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()



def create_ticket_booking_request(CustomerName:str, CustomerPhone:str, CustomerEmail:str) -> requests.Response:
    """
    Sends a ticket booking request to the Pega API and creates a new booking case. Ask user for the details of the customer and create a ticket booking request.
    This function constructs a JSON payload with customer details and sends it to the specified Pega endpoint.
    if any of the required parameters are missing, ask user to provide the details again.

    Args:
        CustomerName (str): The full name of the customer. -- REQUIRED
        CustomerPhone (str): The phone number of the customer.-- REQUIRED
        CustomerEmail (str): The email address of the customer.-- REQUIRED

    Returns:
        requests.Response: The response object from the API request.

    Example:
        >>> response = create_ticket_booking_request("John Doe", "1234567890", "john@gmail.com")
        >>> print(response.status_code)  # Check if the request was successful
        >>> print(response.json())  # View the API response

    Notes:
        - The request sends data to a Pega endpoint using the `POST` method.
        - Ensure that your API key and endpoint are valid.
        - Modify `"caseTypeID"` as per your Pega application structure.
    # """
    url = f"{os.getenv('PEGA_URL')}cases"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {os.getenv('PEGA_KEY')}"  # Ensure this is a valid token
    }
    payload = {
        "content": {
            "pyLabel": "Booking Booking",
            "CustomerEmail": CustomerEmail,
            "CustomerPhone": CustomerPhone,
            "CustomerName": CustomerName
        },
        "caseTypeID": "MyOrg-BookTick-Work-BookTicketReservation"
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    response_data = response.json()
    fin_response = response_data["data"]["caseInfo"]["businessID"]
    print(fin_response)
    return f"Booking request created successfully with ID: {fin_response}"
    

# print(create_ticket_booking_request("John Doe","1234567890","john@gmail.com"))

def get_travel_to_countries() -> list:
    """
    Returns a list of countries that the user can travel to.
    
    Returns:
        list: A list of country names.
    
    Example:
        >>> countries = get_travel_to_countries()
        >>> print(countries)  # Output: ['USA', 'Canada', 'Mexico']
    """
    url  = f"{os.getenv('PEGA_URL')}data_views/D_TravelLocationsList"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {os.getenv('PEGA_KEY')}"  # Ensure this is a valid token
    }
    payload = {}
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response = response.json()
        fin_response = [entry["City"] for entry in response["data"] if "City" in entry]
        return fin_response
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return []

# print(get_travel_to_countries())

def get_booking_details(booking_id:str)->dict:
    """
Fetches detailed booking information from the Pega API using the provided booking ID.
A booking id looks like this - "B-2005"

Args:
    booking_id (str): The unique identifier for the booking to retrieve.

Returns:
    dict: A dictionary containing the complete booking details if successful, or an error message if the retrieval fails.

Example:
    >>> details = get_booking_details("B-12345")
    >>> print(details)
    # Output:
    {
        'classID': 'MyOrg-BookTick-Work-BookTicketReservation',
        'pyLabel': 'Booking Booking',
        'pyID': 'B-2008',
        'pyViewName': '',
        'pyViewContext': '',
        'pxUrgencyWork': 10,
        'pxCreateOperator': 'kartik',
        'pxUpdateDateTime': '2025-05-24T18:28:34.317Z',
        'pxUpdateOperator': 'kartik',
        'pxCreateDateTime': '2025-05-24T18:28:34.301Z',
        'pyStatusWork': 'New',
        'pyCaseLinks': []
    }
    """
    url = f"{os.getenv('PEGA_URL')}cases/MYORG-BOOKTICK-WORK {booking_id}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {os.getenv('PEGA_KEY')}"  # Ensure this is a valid token
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an error for bad responses
        return response.json()["data"]["caseInfo"]["content"]
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": str(e)}
# print(get_booking_details("B-2008"))