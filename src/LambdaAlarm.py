import AlarmCreator


def create_alarms_from_fragment(resource, monitoring_topic, resource_json):
    lambda_dict = {}
    lambda_4xx_count = AlarmCreator.create_alarm(resource, monitoring_topic,
                                                 {'AlarmName': '4xxErrors', 'MetricName': 'Errors',
                                                  'EvaluationPeriods': '1',
                                                  'ComparisonOperator': 'GreaterThanThreshold',
                                                  "Dimensions": [
                                                      {"Name": 'FunctionName', "Value": {"Ref": f'{resource}'}}],
                                                  'Namespace': 'AWS/Lambda', 'Period': '60',
                                                  'Statistic': 'Sum', 'Threshold': 0, 'Unit': 'Count'}, resource_json)
    lambda_invocations_count = AlarmCreator.create_alarm(resource, monitoring_topic,
                                              {'AlarmName': 'Invocations', 'MetricName': 'Invocations',
                                               'EvaluationPeriods': '1',
                                               'ComparisonOperator': 'GreaterThanThreshold',
                                               "Dimensions": [{"Name": 'FunctionName',"Value": {"Ref": f'{resource}'}}],
                                               'Namespace': 'AWS/Lambda', 'Period': '60',
                                               'Statistic': 'Sum', 'Threshold': 0,
                                               'Unit': 'Count'},resource_json)

    lambda_dict.update(lambda_invocations_count)
    lambda_dict.update(lambda_4xx_count)
    return {
        "resources": lambda_dict,
        "stack_params": {
            f'{resource}': {
                "Type": "String",
                "Description": f'Name of the Lambda function identified as {resource} in the parent stack'
            }
        },
        "stack_values": {
            f'{resource}': {
                "Ref": f'{resource}'
            }
        }
    }
