from py2neo import Graph, authenticate
import os
import uuid
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

url = os.environ.get('GRAPHENEDB_BOLT_URL')
username = os.environ.get('GRAPHENEDB_BOLT_USER')
password = os.environ.get('GRAPHENEDB_BOLT_PASSWORD')
http_url = os.environ.get('GRAPHENEDB_URL')


def send_email(recipient, subject, body):
    
    fromaddr = os.environ.get('SMTPUSER')
    username = os.environ.get('SMTPUSER')
    password = os.environ.get('SMTPPW')
    text = MIMEText(body,"plain","utf-8")
    message = MIMEMultipart("alternative")
    message['Subject'] = subject
    message['From'] = fromaddr
    message['To'] = ', '.join(recipient)
    message.attach(text)
    try:
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.ehlo()
        server.starttls()
        server.login(username, password)
        server.sendmail(fromaddr, recipient, message.as_string().encode('ascii'))
        server.close()
        print('Sent email!')
    except Exception as e:
        print(e)
        


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
                send_email(['jonatan.kahrstrom@gmail.com','agnes.tegen@gmail.com'], 
                    u'Ny gäst till bröllopet!', 
                    u"""{0} har anmält sig!
                    Kommentar: {1}
                    Matpreferenser: {2}
                    """.format(request.json.get('name',{}),
                            request.json.get('comment', {}),
                            request.json.get('food', {}))
                    )
                return True
            else:
                query = """MATCH (g:Guest)
                        WHERE g.name = '{0}'
                        SET {1}
                        RETURN g
                        """.format(request.json.get('name',{}), parse_set('g',request.json, ['alcohol','comment','food']))
                guest = graph.data(query)
                send_email(['jonatan.kahrstrom@gmail.com','agnes.tegen@gmail.com'], 
                    u'Bröllopsgäst har ändrat sina uppgifter!', 
                    u"""{0} har uppdaterat uppgifter till:
                    Kommentar: {1}
                    Matpreferenser: {2}
                    """.format(request.json.get('name',{}),
                            request.json.get('comment', {}),
                            request.json.get('food', {}))
                    )
                return True
        except:
            return False

def parse_set(node,json,keys):
    values = ["{0}.{1} = '{2}'".format(node, key, json[key]) for key in json]
    return ", ".join(values)


def parse_request(json):
    values = ["{0} : '{1}'".format(key, json[key]) for key in json]
    return "{" + ", ".join(values) + "}"