from py2neo import Graph, authenticate
import os
import uuid

url = os.environ.get('GRAPHENEDB_BOLT_URL')
username = os.environ.get('GRAPHENEDB_BOLT_USER')
password = os.environ.get('GRAPHENEDB_BOLT_PASSWORD')
http_url = os.environ.get('GRAPHENEDB_URL')

graph = Graph(http_url, username=username, password=password, bolt = False)
#graph = Graph(url, username=username, password=password, bolt = True, secure = True, http_port = 24789, https_port = 24780)

class EntryService:
    def register(self, request):

        try:
            query = """MATCH (g:Guest)
                    WHERE g.name = '{0}'
                    RETURN g
                    """.format(request.json.get('name',{}))
        
            guest = graph.data(query)

            if not guest:

                query = """CREATE (g:Guest {0})
                        WITH g
                        MERGE (w:Wedding {1})
                        MERGE (g) -[:ATTENDING] -> (w)
                        RETURN g""".format(
                            parse_request(request.json),
                            "{name : 'Best wedding ever!'}"
                        )
                guest = graph.data(query)
                return True
            else:
                query = """MATCH (g:Guest)
                        WHERE g.name = '{0}'
                        SET {1}
                        RETURN g
                        """.format(request.json.get('name',{}), parse_set('g',request.json, ['alcohol','comment','food']))
                guest = graph.data(query)
                return True
        except:
            return False

def parse_set(node,json,keys):
    values = ["{0}.{1} = '{2}'".format(node, key, json[key]) for key in json]
    return ", ".join(values)


def parse_request(json):
    values = ["{0} : '{1}'".format(key, json[key]) for key in json]
    return "{" + ", ".join(values) + "}"