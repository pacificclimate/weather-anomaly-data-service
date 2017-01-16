from wads.api.baseline import baseline
from wads.api.weather import weather
from werkzeug.wrappers import BaseResponse as Response
# from flask import Response
import json


method = {
    'baseline': baseline,
    'weather': weather,
}


def dispatch(session, dataset, **kwargs):
    result = method[dataset](session, **kwargs)
    return Response(
        json.dumps(result),
        content_type='application/json'
    )
