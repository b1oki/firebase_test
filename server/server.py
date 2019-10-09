#!python3
# coding: utf-8
"""Server Side FCM sample.

Firebase Cloud Messaging (FCM) can be used to send messages to clients on iOS,
Android and Web.

This sample uses FCM to send two types of messages to clients that are subscribed
to the `news` topic. One type of message is a simple notification message (display message).
The other is a notification message (display notification) with platform specific
customizations. For example, a badge is added to messages that are sent to iOS devices.
"""

import os
import json
import argparse
import json
import requests

from oauth2client.service_account import ServiceAccountCredentials

SERVICE_ACCOUNT_PATH = os.path.dirname(__file__) + '/service-account.json'
with open(SERVICE_ACCOUNT_PATH, 'r') as service_account_file:
    PROJECT_ID = json.load(service_account_file).get('project_id')
BASE_URL = 'https://fcm.googleapis.com'
FCM_ENDPOINT = 'v1/projects/' + PROJECT_ID + '/messages:send'
FCM_URL = BASE_URL + '/' + FCM_ENDPOINT
SCOPES = ['https://www.googleapis.com/auth/firebase.messaging']

# [START retrieve_access_token]


def _get_access_token():
    """Retrieve a valid access token that can be used to authorize requests.

    :return: Access token.
    """

    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        SERVICE_ACCOUNT_PATH, SCOPES)
    access_token_info = credentials.get_access_token()
    return access_token_info.access_token
# [END retrieve_access_token]


def _send_fcm_message(fcm_message):
    """Send HTTP request to FCM with given message.

    Args:
      fcm_message: JSON object that will make up the body of the request.
    """
    # [START use_access_token]
    headers = {
        'Authorization': 'Bearer ' + _get_access_token(),
        'Content-Type': 'application/json; UTF-8',
    }
    # [END use_access_token]
    resp = requests.post(FCM_URL, data=json.dumps(
        fcm_message), headers=headers)

    if resp.status_code == 200:
        print('Message sent to Firebase for delivery, response:')
        print(resp.text)
    else:
        print('Unable to send message to Firebase')
        print(resp.text)


def _build_common_message():
    """Construct common notifiation message.

    Construct a JSON object that will be used to define the
    common parts of a notification message that will be sent
    to any app instance subscribed to the news topic.
    """
    return {
        'message': {
            'topic': 'news',
            'notification': {
                'title': 'FCM Notification',
                'body': 'Notification from FCM'
            }
        }
    }


def _build_override_message():
    """Construct common notification message with overrides.

    Constructs a JSON object that will be used to customize
    the messages that are sent to iOS and Android devices.
    """
    fcm_message = _build_common_message()

    apns_override = {
        'payload': {
            'aps': {
                'badge': 1
            }
        },
        'headers': {
            'apns-priority': '10'
        }
    }

    android_override = {
        'notification': {
            'click_action': 'android.intent.action.MAIN'
        }
    }

    fcm_message['message']['android'] = android_override
    fcm_message['message']['apns'] = apns_override

    return fcm_message


def _build_common_custom_message(title, body, topic, data, link, icon):
    message = {
        'message': {
            'topic': topic,
            'notification': {
                'title': title,
                'body': body
            },
            'data': data,
            'delivery_receipt_requested': True
        }
    }
    if link:
        message['message']['notification']['click_action'] = link
    if icon:
        message['message']['notification']['icon'] = icon
    return message


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--message')
    args = parser.parse_args()
    if args.message and args.message == 'common-message':
        common_message = _build_common_message()
        print('FCM request body for message using common notification object:')
        print(json.dumps(common_message, indent=2))
        _send_fcm_message(common_message)
    elif args.message and args.message == 'override-message':
        override_message = _build_override_message()
        print('FCM request body for override message:')
        print(json.dumps(override_message, indent=2))
        _send_fcm_message(override_message)
    elif args.message:
        print('Send custom message.')
        message_params = json.loads(args.message)
        common_message = _build_common_custom_message(
            title=message_params.get('title'),
            body=message_params.get('body'),
            topic=message_params.get('topic'),
            data=message_params.get('data'),
            link=message_params.get('link'),
            icon=message_params.get('icon')
        )
        print('FCM request body for message using common notification object:')
        print(json.dumps(common_message, indent=2))
        _send_fcm_message(common_message)
    else:
        print('''Invalid command. Please use one of the following commands:
python messaging.py --message=common-message
python messaging.py --message=override-message''')


if __name__ == '__main__':
    main()
