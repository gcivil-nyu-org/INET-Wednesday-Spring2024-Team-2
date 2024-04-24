# utils.py

import boto3
from django.conf import settings
from pathlib import Path
import os


def send_email_to_admin(username,email):
    ses_client = boto3.client(
        'ses',
        # region_name=settings.AWS_SES_REGION_NAME,
        # aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        # aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        region_name="us-east-1",
        aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID") ,
        aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
    )

    SUBJECT = "New Landlord Signup Notification"
    # BODY_TEXT = (f"A landlord with username '{username}' has signed up. Please verify their documentation and approve them.")
    BODY_TEXT = (f"In rentwisenyc, a landlord with username '{username}' and email '{email}' has signed up. Please verify their documentation and approve them. Access it at url http://rent-wise-env.eba-3qbiyspq.us-east-1.elasticbeanstalk.com/admin ")
    CHARSET = "UTF-8"
    response = None
    
    try:
        response = ses_client.send_email(
            Destination={
                'ToAddresses': [
                    'rentwisenyc@gmail.com',
                ],
            },
            Message={
                'Body': {
                    'Text': {
                        'Charset': CHARSET,
                        'Data': BODY_TEXT,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source='rentwisenyc@gmail.com',
        )
    except Exception as e:
        print(f"Error sending email: {e}")
        response = {"Error": "Failed to send email", "Exception": str(e)}

    return response
