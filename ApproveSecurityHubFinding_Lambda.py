import os
import boto3

def lambda_handler(event, context):
    print('Action request received from API Gateway')

    try:
        
        #Extract validated query strings from the event object
        id = event['queryStringParameters']['id']
        arn = event['queryStringParameters']['arn']
        action = event['queryStringParameters']['action']
        target = event['queryStringParameters']['target']  
        
        # Create a SecurityHub client
        securityhub = boto3.client('securityhub')

        # Define the updates for the findings
        updates = {
            'FindingIdentifiers': [
                {
                    'Id': id,
                    'ProductArn': arn
                }
            ],
            'Note': {
                'Text': 'Updated after review.',
                'UpdatedBy': 'security_operator@example.com'
            },
            'Workflow': {
                'Status': 'RESOLVED' if action.lower() == 'approved' else 'NOTIFIED'
            }
        }
        
        if action.lower() == 'deny':
            # Create an S3 client
            s3 = boto3.client('s3')

            # Configure the logging parameters
            logging_config = {
                'LoggingEnabled': {
                    'TargetBucket': os.environ('DEFAULT_LOGGING_BUCKET'), #TODO Bucket where logs are stored, set to default
                    'TargetPrefix': os.environ('DEFAULT_LOGGING_PREFIX') #TODO Required prefix for log files, e.g. logs/
                }
            }

            # Enable server access logging
            s3.put_bucket_logging(
                Bucket=target,
                BucketLoggingStatus=logging_config
            )
            print(f'Server access logging enabled for bucket {target}')
        
        # Batch update findings
        response = securityhub.batch_update_findings(**updates)
        print("Batch update successful:", response)
        
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "text/plain"
            },
            "body": "Finding successfully updated"
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "text/plain"
            },
            "body": "Failed to update findings: " + str(e)
        }
