from rest_framework.response import Response


def success_response(message="successful operation", data=None, status=200):
    response_data = {
        "success":True,
        "message": message,
    }
    if data:
        response_data["data"] = data
    return Response(response_data, status=status)

def error_response(message="something went wrong", errors=None, status=400):
    response_data = {
        "success":False,
        "message": message
    }
    if errors:
        response_data["errors"] = errors
    return Response(response_data, status=status)