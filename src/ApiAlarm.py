import AlarmCreator


def create_alarms_from_fragment(resource, monitoring_topic, resource_json):
    api_dict = {}
    api_5xx_count = AlarmCreator.create_alarm(resource, monitoring_topic,
                                                 {'AlarmName': '5XXErrors', 'MetricName': '5XXError',
                                                  'EvaluationPeriods': '1',
                                                  'ComparisonOperator': 'GreaterThanThreshold',
                                                  "Dimensions": [
                                                      {"Name": 'ApiName', "Value": {"Ref": f'{resource}'}}],
                                                  'Namespace': 'AWS/ApiGateway', 'Period': '300',
                                                  'Statistic': 'Sum', 'Threshold': 0, 'Unit': 'Count'}, resource_json)

    api_4xx_count = AlarmCreator.create_alarm(resource, monitoring_topic,
                                              {'AlarmName': '4XXErrors', 'MetricName': '4XXError',
                                               'EvaluationPeriods': '2',
                                               'ComparisonOperator': 'GreaterThanThreshold',
                                               "Dimensions": [
                                                   {"Name": 'ApiName', "Value": {"Ref": f'{resource}'}}],
                                               'Namespace': 'AWS/ApiGateway', 'Period': '300', 'Statistic': 'Sum',
                                               'Threshold': 5, 'Unit': 'Count', 'DatapointsToAlarm': 2}, resource_json)

    api_dict.update(api_5xx_count)
    api_dict.update(api_4xx_count)
    return {
        "resources": api_dict,
        "stack_params": {
            f'{resource}': {
                "Type": "String",
                "Description": f'Name of the Api identified as {resource} in the parent stack'
            }
        },
        "stack_values": {
            f'{resource}': {
                "Ref": f'{resource}'
            }
        }
    }