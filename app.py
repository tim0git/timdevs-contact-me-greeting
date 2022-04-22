import json
import logging
import os
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_email_template():
    SUBJECT = "Amazon SES Test (SDK for Python)"

    BODY_TEXT = ("Amazon SES Test (Python)\r\n"
                 "This email was sent with Amazon SES using the "
                 "AWS SDK for Python (Boto)."
                 )

    BODY_HTML = """<html>
<head></head>
<body>
  <h1>Amazon SES Test (SDK for Python)</h1>
  <p>This email was sent with
    <a href='https://aws.amazon.com/ses/'>Amazon SES</a> using the
    <a href='https://aws.amazon.com/sdk-for-python/'>
      AWS SDK for Python (Boto)</a>.</p>
</body>
</html>
            """

    template = {
        "SUBJECT": SUBJECT,
        "BODY_TEXT": BODY_TEXT,
        "BODY_HTML": BODY_HTML
    }
    return template


def get_name_from_dynamodb(event):
    name = event["Records"][0]["dynamodb"]["NewImage"]["Name"]["S"]
    return name


def get_email_from_dynamodb(event):
    email = event["Records"][0]["dynamodb"]["NewImage"]["Email"]["S"]
    return email


def get_env_vars():
    return {
        "CHARSET": os.environ.get("CHARSET"),
        "SENDER": os.environ.get("SENDER")
    }


def send_email(email, name, charset, sender, subject, body_text, body_html):
    client = boto3.client('ses', region_name=os.environ.get('AWS_REGION'))
    logger.info("Sending email to Name: " + name + " " + "at address Email: " + email)
    try:
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    email,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': charset,
                        'Data': body_html,
                    },
                    'Text': {
                        'Charset': charset,
                        'Data': body_text,
                    },
                },
                'Subject': {
                    'Charset': charset,
                    'Data': subject,
                },
            },
            Source=sender,
        )
    except ClientError as e:
        logger.error(e.response['Error']['Message'])
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'error'})
        }
    else:
        logger.info("Email sent message ID: {}".format(response['MessageId']))
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'success', "messageId": response['MessageId']})
        }


def lambda_handler(event, context):
    logger.info("Received event")

    env_vars = get_env_vars()
    email = get_email_from_dynamodb(event)
    name = get_name_from_dynamodb(event)
    template = get_email_template()

    return send_email(email,
                      name,
                      env_vars["CHARSET"],
                      env_vars["SENDER"],
                      template["SUBJECT"],
                      template["BODY_TEXT"],
                      template["BODY_HTML"]
                      )
