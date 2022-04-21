import logging
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event):
    logger.info("Received event")
    logger.info(json.dumps(event))
    try:
        return {
            "statusCode": 200,
            'body': json.dumps({'message': 'success'})
        }
    except Exception as e:
        logger.error(str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'error'})
        }

