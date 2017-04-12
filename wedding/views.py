from .errorhandler import InvalidUsage
from flask import Flask, request, session, redirect, jsonify, abort, url_for
from .services import EntryService, graph
from urllib.parse import unquote
import itertools
from operator import itemgetter

# Initialize app...
app = Flask(__name__)

# Setup services...
entryService = EntryService()

# Handle invalid requests
@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

# Registers a guest
@app.route('/api/v1/guest/register/', methods=['POST'])
def register_guest():
    print("hej")
    return jsonify(data=entryService.register(request))

@app.route('/api/v1/site-map')
def list_routes():
    output = []
    for rule in app.url_map.iter_rules():

        options = {}
        for arg in rule.arguments:
            options[arg] = "[{0}]".format(arg)

        methods = ','.join(set(rule.methods) - set(['OPTIONS', 'HEAD']))
        url = url_for(rule.endpoint, **options)
        line = {'rule': unquote(rule.endpoint), 'methods': unquote(methods), 'url': unquote(url)}
        output.append(line)
    
    output.sort(key=itemgetter("url"))
    retval = []
    for key, group in itertools.groupby(output, lambda item: item["url"]):
        retval.append({'url': key, 'methods': ', '.join([item["methods"] for item in group])})

    return jsonify(data=retval)