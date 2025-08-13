#!/usr/bin/env python3
import sys
import os

from flask import *

from fido2.server import Fido2Server
from fido2.webauthn import PublicKeyCredentialRpEntity, PublicKeyCredentialUserEntity
from fido2.attestation import UntrustedAttestation
from fido2.mds3 import MdsAttestationVerifier, parse_blob
import base64 
from cryptography.fernet import Fernet
import time
import json
import requests

app = Flask(__name__, static_url_path="")
app.secret_key = os.urandom(32)  
rp = PublicKeyCredentialRpEntity(name="Demo server", id="$$domainname$$")




basepath='/var/cahicha'
#os.system(f'mkdir -p {basepath}')

ca = b64decode(
    """
MIIDXzCCAkegAwIBAgILBAAAAAABIVhTCKIwDQYJKoZIhvcNAQELBQAwTDEgMB4G
A1UECxMXR2xvYmFsU2lnbiBSb290IENBIC0gUjMxEzARBgNVBAoTCkdsb2JhbFNp
Z24xEzARBgNVBAMTCkdsb2JhbFNpZ24wHhcNMDkwMzE4MTAwMDAwWhcNMjkwMzE4
MTAwMDAwWjBMMSAwHgYDVQQLExdHbG9iYWxTaWduIFJvb3QgQ0EgLSBSMzETMBEG
A1UEChMKR2xvYmFsU2lnbjETMBEGA1UEAxMKR2xvYmFsU2lnbjCCASIwDQYJKoZI
hvcNAQEBBQADggEPADCCAQoCggEBAMwldpB5BngiFvXAg7aEyiie/QV2EcWtiHL8
RgJDx7KKnQRfJMsuS+FggkbhUqsMgUdwbN1k0ev1LKMPgj0MK66X17YUhhB5uzsT
gHeMCOFJ0mpiLx9e+pZo34knlTifBtc+ycsmWQ1z3rDI6SYOgxXG71uL0gRgykmm
KPZpO/bLyCiR5Z2KYVc3rHQU3HTgOu5yLy6c+9C7v/U9AOEGM+iCK65TpjoWc4zd
QQ4gOsC0p6Hpsk+QLjJg6VfLuQSSaGjlOCZgdbKfd/+RFO+uIEn8rUAVSNECMWEZ
XriX7613t2Saer9fwRPvm2L7DWzgVGkWqQPabumDk3F2xmmFghcCAwEAAaNCMEAw
DgYDVR0PAQH/BAQDAgEGMA8GA1UdEwEB/wQFMAMBAf8wHQYDVR0OBBYEFI/wS3+o
LkUkrk1Q+mOai97i3Ru8MA0GCSqGSIb3DQEBCwUAA4IBAQBLQNvAUKr+yAzv95ZU
RUm7lgAJQayzE4aGKAczymvmdLm6AC2upArT9fHxD4q/c2dKg8dEe3jgr25sbwMp
jjM5RcOO5LlXbKr8EpbsU8Yt5CRsuZRj+9xTaGdWPoO4zzUhw8lo/s7awlOqzJCK
6fBdRoyV3XpYKBovHd7NADdBj+1EbddTKJd+82cEHhXXipa0095MJ6RMG3NzdvQX
mcIfeg7jLQitChws/zyrVQ4PkX4268NXSb7hLi18YIvDQVETI53O9zJrlAGomecs
Mx86OyXShkDOOyyGeMlhLxS67ttVb9+E7gUJTb0o2HLO02JQZR7rkpeDMdmztcpH
WD9f"""
)

mds=None

def getMds():
    global mds
    mdsurl='https://mds3.fidoalliance.org/'
    resp=requests.get(mdsurl)
    resptext=resp.content
    metadata=parse_blob(resptext, ca)
    mds=MdsAttestationVerifier(metadata)
    
getMds()
server = Fido2Server(rp, attestation='direct', verify_attestation=mds,)

secret={}

def save_secret():
    global secret
    filename='secret.sec'
    secret2={}
    secret2['key']=base64.b64encode(secret['key']).decode()
    secret2['timestamp']=base64.b64encode(secret['timestamp']).decode()
    with open(os.path.join(basepath, filename), 'w') as file:
        file.write(json.dumps(secret2))
        print('File saved')
        print(file)
    
def read_secret():
    global secret
    global secret
    filename='secret.sec'
    secret2={}
    try:
         with open(os.path.join(basepath, filename), 'r') as file:
              secret2=json.loads(file.read())
              secret['key']=base64.b64decode(secret2['key'])
              secret['timestamp']=base64.b64decode(secret2['timestamp'])
    except:
        gen_secret()



def get_currenttime():
    timestamp=str(int(time.time()))
    return timestamp.encode()
    
def timestamp_expired(timestamp, expiry=86400):
    timestamp=int(timestamp.decode())
    current_time=int(time.time())
    return (current_time-timestamp)>=expiry

def gen_secret():
    global secret
    secret['key']=Fernet.generate_key()
    secret['timestamp']=get_currenttime()
    save_secret()

def get_username():
    return 'cahicha_'+base64.b64encode(b'human').decode()   
    
def get_token():
    global secret
    if not secret:
        read_secret()        
    if 'key' not in secret or 'timestamp' not in secret or timestamp_expired(secret['timestamp']):
        gen_secret()
    f=Fernet(secret['key'])
    secretheader='cahichavalid'.encode()
    nonce=os.urandom(16)
    timestamp=get_currenttime()
    token=f.encrypt(secretheader+nonce+timestamp)
    return 'cahicha_human_'+token.decode()
    
def validate_token(token):
    global secret
    print('Validating ',token)
    if not secret:
        read_secret()        
    if 'key' not in secret or 'timestamp' not in secret or timestamp_expired(secret['timestamp']):
        print('New secrets generated while validation')
        gen_secret()
        return False
    f=Fernet(secret['key'])
    startwith='cahicha_human_'
    secretheader='cahichavalid'.encode()
    if not token.startswith(startwith):
        print('Header not found')
        return False
    token=token[len(startwith):]
    decrypted=b''
    try:
        decrypted=f.decrypt(token.encode())
        print('Decryption success')
    except:
        print('Decryption fail')
        return False
    if not decrypted.startswith(secretheader):
        print('Decrypted header fail')
        return False
    print(decrypted)
    decrypted=decrypted[len(secretheader):]
    decrypted=decrypted[16:]
    print('Testing timestamp ', decrypted)
    if timestamp_expired(decrypted):
        print('Expired')
        return False
    print('Validation success')
    return True
    
    
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    full_path=f'/{path}' if path else '/'
    if request.query_string:
        full_path +=f'?{request.query_string.decode()}'
    return redirect(f'/cahichacheck?next={full_path}')
    
@app.route('/cahichacheck')
def checkpage():
    original_path=request.args.get('next', '/')
    validationcookie=request.cookies.get('cahicha_token', '')
    if validate_token(validationcookie):
        return redirect(original_path)
    return render_template('template.html', next=original_path)
    
@app.route('/cahichafinal', methods=['POST'])
def cahichafinal():
    nextto=request.form.get('next', '/')
    return redirect(nextto)
        

@app.route("/api/register/begin", methods=["POST"])
def register_begin():
    username=request.cookies.get('cahichaname', get_username())
    credentials=[]
    options, state = server.register_begin(
        PublicKeyCredentialUserEntity(
            id=username.encode(),
            name="CAHICHA Verification",
            display_name="CAHICHA Verification",
        ),
        credentials,
        user_verification="discouraged"
    )

    session["state"] = state
    print("\n\n\n\n")
    print(dict(options))
    print("\n\n\n\n")

    resp= make_response(jsonify(dict(options)))
    resp.set_cookie('cahichaname', username, max_age=10*365*24*3600)
    return resp


@app.route("/api/register/complete", methods=["POST"])
def register_complete():
    username=request.cookies.get('cahichaname', get_username())
    credentials=[]
    response = request.json
    print("RegistrationResponse:", response)
    auth_data = server.register_complete(session["state"], response)

    credentials.append(auth_data.credential_data)
    print("REGISTERED CREDENTIAL:", auth_data.credential_data)
    resp= make_response(jsonify({"status": "OK"}))
    resp.set_cookie('cahicha_token', get_token(), httponly=True)
    return resp
    
@app.route("/validate", methods=["POST"])
def validate():
    token=request.form.get('token', '')
    try:
        if validate_token(token):
            return 'valid'
        return 'invalid'
    except:
        return 'invalid'
