import json
import decimal
import datetime

class CustomJSONEncoder(json.JSONEncoder):
    """
    JSON Encoder that handles Decimal, Date, and DateTime objects
    """
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        return super(CustomJSONEncoder, self).default(obj)

def json_dumps(data, indent=None):
    """Helper function to dump JSON with custom encoder"""
    return json.dumps(data, cls=CustomJSONEncoder, indent=indent)
