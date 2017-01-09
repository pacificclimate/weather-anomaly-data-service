from wads.api.baseline import baseline
from wads.api.weather import weather
from werkzeug.wrappers import BaseResponse as Response
# from flask import Response
import json

datasets = {
    'baseline': baseline,
    'weather': weather,
}


def dispatch(session, dataset, **kwargs):
    result = datasets[dataset](session, **kwargs)
    return Response(
        json.dumps(result),
        content_type='application/json'
    )