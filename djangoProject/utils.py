import json
from djangoProject.exceptions import ValidationError


def parse_json_body(request):
    """Parse JSON body request"""
    try:
        return json.loads(request.body)
    except json.JSONDecodeError:
        raise ValidationError("Invalid JSON format")
