import pytest
import app


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


# Success
def test_returns_status_code_200_if_successful(apigw_event):
    ret = app.lambda_handler(apigw_event)
    assert ret["statusCode"] == 200
