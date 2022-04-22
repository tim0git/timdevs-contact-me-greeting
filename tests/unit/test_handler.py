import json
import os
import boto3
from moto import mock_ses
import pytest
import app
from testfixtures import log_capture
import logging


@pytest.fixture()
def apigw_event():
    """ Generates API GW Event"""
    return {
        "Records": [
            {
                "eventID": "bb30e13175ffad6d978d51952a9c850b",
                "eventName": "INSERT",
                "eventVersion": "1.1",
                "eventSource": "aws:dynamodb",
                "awsRegion": "eu-west-1",
                "dynamodb": {
                    "ApproximateCreationDateTime": 1650558395,
                    "Keys": {
                        "Email": {
                            "S": "test@gmail.com"
                        },
                        "ID": {
                            "S": "eaed588b-1a91-413e-818d-9e01dbaa2f89"
                        }
                    },
                    "NewImage": {
                        "Email": {
                            "S": "test@gmail.com"
                        },
                        "Message": {
                            "S": "hello from postman custom domian success"
                        },
                        "ID": {
                            "S": "eaed588b-1a91-413e-818d-9e01dbaa2f89"
                        },
                        "TTL": {
                            "N": "1653150394"
                        },
                        "Name": {
                            "S": "test"
                        }
                    },
                    "SequenceNumber": "163800500000000045865059133",
                    "SizeBytes": 178,
                    "StreamViewType": "NEW_IMAGE"
                },
                "eventSourceARN": "arn:aws:dynamodb:eu-west-1:123456789:table/timdevs-contact-me-staging/stream/2022-01-21T12:00:00.000"
            }
        ]
    }


verified_email = 'sender@example.com'
unverified_email = 'sender@unverifiedemail.com'

os.environ['SENDER'] = 'Sender Name <{}>'.format(verified_email)
os.environ['AWS_REGION'] = 'eu-west-1'
os.environ['CHARSET'] = 'UTF-8'


def set_up_email_client(email_address):
    client = boto3.client("ses", region_name=os.environ['AWS_REGION'])

    client.verify_email_address(
        EmailAddress=email_address
    )
    return client


# Success
@mock_ses
def test_returns_status_code_200_if_successful(apigw_event):
    set_up_email_client(verified_email)
    res = app.lambda_handler(apigw_event, "")
    assert res['statusCode'] == 200


@mock_ses
def test_returns_message_id_if_successful(apigw_event):
    set_up_email_client(verified_email)
    res = app.lambda_handler(apigw_event, "")
    body = json.loads(res["body"])
    assert isinstance(body['messageId'], str)


@mock_ses
def test_ses_attempts_delivery_if_successful(apigw_event):
    client = set_up_email_client(verified_email)
    app.lambda_handler(apigw_event, "")
    response = client.get_send_statistics()
    send_data_points = response['SendDataPoints']
    assert send_data_points[0]["DeliveryAttempts"] == 1


# Error
@mock_ses
def test_returns_status_code_500_if_unsuccessful(apigw_event):
    set_up_email_client(unverified_email)
    res = app.lambda_handler(apigw_event, "")
    assert res['statusCode'] == 500


@mock_ses
def test_returns_error_message_if_unsuccessful(apigw_event):
    set_up_email_client(unverified_email)
    res = app.lambda_handler(apigw_event, "")
    body = json.loads(res["body"])
    assert body["message"] == "error"


@mock_ses
def test_ses_does_not_attempt_delivery_if_from_email_is_not_verified(apigw_event):
    client = set_up_email_client(unverified_email)
    app.lambda_handler(apigw_event, "")
    response = client.get_send_statistics()
    send_data_points = response['SendDataPoints']
    assert send_data_points[0]["DeliveryAttempts"] == 0


# Logging
credential_log = ('botocore.credentials', 'INFO', 'Found credentials in environment variables.')
event_received_log = ('root', 'INFO', 'Received event')
sending_test_email_log = ('root', 'INFO', 'Sending email to Name: test at address Email: test@gmail.com')


@mock_ses
@log_capture(level=logging.INFO)
def test_logs_info_request_and_success(capture, apigw_event):
    set_up_email_client(verified_email)
    res = app.lambda_handler(apigw_event, "")
    body = json.loads(res["body"])

    capture.check(
        credential_log,
        event_received_log,
        sending_test_email_log,
        ('root', 'INFO', 'Email sent message ID: {}'.format(body['messageId'])),
    )


@mock_ses
@log_capture(level=logging.INFO)
def test_logs_info_request_and_error_when_sender_email_is_unverified(capture, apigw_event):
    set_up_email_client(unverified_email)
    app.lambda_handler(apigw_event, "")

    capture.check(
        credential_log,
        event_received_log,
        sending_test_email_log,
        ('root', 'ERROR', 'Email address not verified Sender Name <{}>'.format(verified_email)),
    )
