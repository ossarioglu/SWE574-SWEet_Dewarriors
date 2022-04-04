import requests
from django.http import JsonResponse
from decouple import config


class LocationService:
    BASE_URL = 'https://maps.googleapis.com/maps/api/place/textsearch/json?key=' + config('GOOGLE_API_KEY') + '&query='

    @staticmethod
    def search(query: str) -> JsonResponse:
        request_uri = LocationService.BASE_URL + query

        return LocationService.__return_json_response(request_uri)

    @staticmethod
    def __return_json_response(request_uri, payload={}, headers={}):
        response = requests.request('GET', request_uri, headers=headers, data=payload)

        return JsonResponse({'response': response.json()})
