import AlarmCreator


def create_alarms_from_fragment(resource, monitoring_topic, resource_json):
    dynamo_dict = {}
    if 'ProvisionedThroughput' in resource_json['Properties']:
        provisioned_read = resource_json['Properties']['ProvisionedThroughput']['ReadCapacityUnits']
        if not isinstance(provisioned_read, dict):
            read_capacity = AlarmCreator.create_alarm(resource, monitoring_topic,
                                                      {'AlarmName': 'ReadCapacityUnitsLimitAlarm',
                                                       'MetricName': 'ConsumedReadCapacityUnits',
                                                       'EvaluationPeriods': '1',
                                                       'ComparisonOperator': 'GreaterThanOrEqualToThreshold',
                                                       "Dimensions": [
                                                           {"Name": 'TableName', "Value": {"Ref": f'{resource}'}}],
                                                       'Namespace': 'AWS/DynamoDB ',
                                                       'Period': '60',
                                                       'Statistic': 'Sum', 'Threshold': int(provisioned_read * 60 * 0.8),
                                                       'Unit': 'Count'}, resource_json)
            dynamo_dict.update(read_capacity)

        provisioned_write = resource_json['Properties']['ProvisionedThroughput']['WriteCapacityUnits']
        if not isinstance(provisioned_write, dict):
            write_capacity = AlarmCreator.create_alarm(resource, monitoring_topic,
                                                       {'AlarmName': 'WriteCapacityUnitsLimitAlarm',
                                                        'MetricName': 'ConsumedWriteCapacityUnits',
                                                        'EvaluationPeriods': '1',
                                                        'ComparisonOperator': 'GreaterThanOrEqualToThreshold',
                                                        "Dimensions": [
                                                            {"Name": 'TableName', "Value": {"Ref": f'{resource}'}}],
                                                        'Namespace': 'AWS/DynamoDB ',
                                                        'Period': '60',
                                                        'Statistic': 'Sum', 'Threshold': provisioned_write * 60 * 0.8,
                                                        'Unit': 'Count'}, resource_json)
            dynamo_dict.update(write_capacity)
        return {
            "resources": dynamo_dict,
            "stack_params": {
                resource: {
                    "Type": "String",
                    "Description": 'Name of the Dynamo table identified as {} in the parent stack'.format(resource)
                }
            },
            "stack_values": {
                resource: {
                    "Ref": f'{resource}'
                }
            }
        }
    return {
        "resources": {},
        "stack_params": {},
        "stack_values": {}
    }
