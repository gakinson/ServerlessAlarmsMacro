# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import os
import logging
import uuid
import boto3
import LambdaAlarm, DynamoAlarm

logger = logging.getLogger()
logger.setLevel(logging.INFO)
SNS_TOPIC_PARAM = 'AlarmsSNSArn'
DISABLE_ALARMS_PARAM = 'AlarmsDisabled'
s3 = boto3.client("s3")


def handler(event, context):
    try:
        fragment = event["fragment"]
        parameters = event['templateParameterValues']
        if DISABLE_ALARMS_PARAM in parameters and parameters[DISABLE_ALARMS_PARAM]:
            resp = {
                'requestId': event['requestId'],
                'status': 'success',
                'fragment': fragment
            }
            return resp

        if SNS_TOPIC_PARAM in parameters:
            monitoring_topic_arn = parameters[SNS_TOPIC_PARAM]
        else:
            resp = {
                'requestId': event['requestId'],
                'status': 'failure',
                'fragment': fragment,
                'errorMessage': f'Missing parameter {SNS_TOPIC_PARAM} in the main template'
            }
            return resp

        logger.info('Input Template: {}'.format(fragment))

        lambda_alarm_dictionary = {}
        lambda_stack_params = {
            "TopicArn": {
                "Type": "String",
                "Description": "The ARN for the SNS topic for the CloudWatch Alarms"
            }
        }

        lambda_stack_values = {
            "TopicArn": f'{monitoring_topic_arn}'
        }

        dynamo_alarm_dictionary = {}
        dynamo_stack_params = lambda_stack_params.copy()
        dynamo_stack_values = lambda_stack_values.copy()

        resources = fragment['Resources']
        for resource in resources:
            logger.info('Searching {} for resource type'.format(resource))
            resource_json = resources[resource]
            try:
                if resource_json['Type'] == 'AWS::Lambda::Function' or resource_json[
                    'Type'] == 'AWS::Serverless::Function':
                    logger.info('Resource {} is a lambda function'.format(resource))
                    lambda_alarm_resources = LambdaAlarm.create_alarms_from_fragment(resource, "TopicArn",
                                                                                     resource_json)
                    lambda_alarm_dictionary.update(lambda_alarm_resources['resources'])
                    lambda_stack_params.update(lambda_alarm_resources['stack_params'])
                    lambda_stack_values.update(lambda_alarm_resources['stack_values'])

                elif resource_json['Type'] == 'AWS::DynamoDB::Table':
                    logger.info('Resource {} is a dynamo table'.format(resource))
                    dynamo_alarm_resources = DynamoAlarm.create_alarms_from_fragment(resource, "TopicArn",
                                                                                     resource_json)
                    dynamo_alarm_dictionary.update(dynamo_alarm_resources['resources'])
                    dynamo_stack_params.update(dynamo_alarm_resources['stack_params'])
                    dynamo_stack_values.update(dynamo_alarm_resources['stack_values'])

                elif resource_json['Type'] == 'AWS::Serverless::Api':
                    logger.info('Resource {} is a serverless api'.format(resource))
                    # dynamo_alarm_dictionary.update(DynamoAlarm.create_alarms_from_fragment(resource, "TopicArn", resource_json))
                else:
                    logger.info('Resource {} is not of a supported resource type'.format(resource))
            except Exception as e:
                logger.error('ERROR {}'.format(e))
                resp = {
                    'requestId': event['requestId'],
                    'status': 'failure',
                    'fragment': fragment,
                    'errorMessage': 'ERROR {}'.format(e)
                }
                return resp

        # sns_topic = {
        #     f'{monitoring_topic}': {
        #         "Type": "AWS::SNS::Topic",
        #         "DeletionPolicy": "Retain",
        #         "Properties": {
        #             "TopicName": f'{monitoring_topic_name}'
        #         }
        #     }
        # }
        # resources.update(sns_topic)

        if len(lambda_alarm_dictionary) > 0:
            lambda_nested_stack = {
                "ServerlessAlarmsMacroLambdaStack": create_nested_stack(lambda_alarm_dictionary, lambda_stack_params,
                                                                        lambda_stack_values)
            }
            resources.update(lambda_nested_stack)
        if len(dynamo_alarm_dictionary) > 0:
            dynamo_nested_stack = {
                "ServerlessAlarmsMacroDynamoStack": create_nested_stack(dynamo_alarm_dictionary, dynamo_stack_params,
                                                                        dynamo_stack_values)
            }
            resources.update(dynamo_nested_stack)

        logger.info('Final Template: {}'.format(fragment))

        # Send Response to stack
        resp = {
            'requestId': event['requestId'],
            'status': 'success',
            'fragment': fragment
        }
        return resp
    except Exception as error:
        logger.error('ERROR {}'.format(error))
        resp = {
            'requestId': event['requestId'],
            'status': 'failure',
            'fragment': fragment,
            'errorMessage': 'ERROR {}'.format(error)
        }
        return resp


def create_nested_stack(resources, parameters, parameter_values):
    bucket = os.environ['BUCKET']
    key = str(uuid.uuid4()) + '.template'
    stack = {
        "AWSTemplateFormatVersion": "2010-09-09",
        "Description": "Nested stack with auto-generated Alarms",
        "Resources": resources,
        "Parameters": parameters
    }

    s3.put_object(Bucket=bucket, Key=key, Body=str(stack))
    url = s3.generate_presigned_url('get_object', Params={'Bucket': bucket, 'Key': key}, ExpiresIn=10800)

    # location = s3.get_bucket_location(Bucket=bucket)['LocationConstraint']
    # url = "https://s3-%s.amazonaws.com/%s/%s" % (location, bucket, key)

    stack_resource = {
        "Type": "AWS::CloudFormation::Stack",
        "Properties": {
            "TemplateURL": url,
            "Parameters": parameter_values
        }
    }

    return stack_resource
