import os
import base64
import requests
from ms_graph import generate_access_token

def draft_attachment(file_path):
    if not os.path.exists(file_path):
        print('file is not found')
        return
    
    with open(file_path, 'rb') as upload:
        media_content = base64.b64encode(upload.read())
        
    data_body = {
        '@odata.type': '#microsoft.graph.fileAttachment',
        'contentBytes': media_content.decode('utf-8'),
        'name': os.path.basename(file_path)
    }
    return data_body
def sendOutlook(to, subject, body):

    APP_ID = '1389be5f-0dac-4315-ac68-bcd99d6160c0'
    SCOPES = ['Mail.Send', 'Mail.ReadWrite']

    access_token = generate_access_token(app_id=APP_ID, scopes=SCOPES)
    headers = {
        'Authorization': 'Bearer ' + access_token['access_token']
    }


    request_body = {
        'message': {
            # recipient list
            'toRecipients': [
                {
                    'emailAddress': {
                        'address': to
                    }
                }
            ],
            # email subject
            'subject': subject,
            'importance': 'normal',
            'body': {
                'contentType': 'HTML',
                'content': f'<b>{body}</b>'
            }
            
        }
    }
    '''
    # include attachments
            'attachments': [
                draft_attachment('hello.txt'),
                draft_attachment('image.png')
            ]
    '''

    GRAPH_ENDPOINT = 'https://graph.microsoft.com/v1.0'
    endpoint = GRAPH_ENDPOINT + '/me/sendMail'

    response = requests.post(endpoint, headers=headers, json=request_body)
    if response.status_code == 202:
        print('Email sent')
    else:
        print(response.reason)
    return response