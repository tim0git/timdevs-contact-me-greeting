import json
import logging
import os
import boto3
from botocore.exceptions import ClientError
from aws_xray_sdk.core import xray_recorder

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@xray_recorder.capture("get_name_from_dynamodb")
def get_name_from_dynamodb(event):
    name = event["Records"][0]["dynamodb"]["NewImage"]["Name"]["S"]
    return name


@xray_recorder.capture("get_email_from_dynamodb")
def get_email_from_dynamodb(event):
    email = event["Records"][0]["dynamodb"]["NewImage"]["Email"]["S"]
    return email


@xray_recorder.capture("send_email")
def send_email(email, name):
    client = boto3.client('ses', region_name=os.environ.get('AWS_REGION'))
    logger.info("Sending email to Name: " + name + " " + "at address Email: " + email)
    try:
        response = client.send_templated_email(
            Source=os.environ.get("SENDER"),
            Destination={
                'ToAddresses': [
                    email,
                ],
            },
            Template=os.environ.get('TEMPLATE_NAME'),
            TemplateData=json.dumps({
                "name": name
            })
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

    email = get_email_from_dynamodb(event)
    name = get_name_from_dynamodb(event)

    return send_email(email, name)
