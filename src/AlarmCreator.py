
def create_alarm(resource,monitoring_topic,alarm,resource_json):
    alarm_template = {f'{resource}{alarm["AlarmName"]}': {
        "Type": "AWS::CloudWatch::Alarm",
        "Properties": {
            "ActionsEnabled": "true",
            "AlarmActions": [{
                "Ref": f'{monitoring_topic}'
            }],
            # "InsufficientDataActions": [{
            #     "Ref": f'{monitoring_topic}'
            # }],
            "AlarmDescription": {
                "Fn::Join": [
                    " - ", [
                        f'{alarm["MetricName"]}',
                        {
                            "Ref": f'{resource}'
                        }
                    ]
                ]
            },
            "AlarmName": {
                "Fn::Join": [
                    "-", [
                        {
                            "Ref": "AWS::StackName"
                        },
                        f'{resource}',
                        f'{alarm["MetricName"]}'
                    ]
                ]
            },
            'EvaluationPeriods': f'{alarm["EvaluationPeriods"]}',
            "ComparisonOperator": f'{alarm["ComparisonOperator"]}',
            "Dimensions": alarm["Dimensions"],
            "MetricName": f'{alarm["MetricName"]}',
            "Namespace": f'{alarm["Namespace"]}',
            "Period": f'{alarm["Period"]}',
            "Statistic": f'{alarm["Statistic"]}',
            "Threshold": f'{alarm["Threshold"]}',
            "Unit": f'{alarm["Unit"]}'
        }
    }}
    if 'DatapointsToAlarm' in alarm:
        alarm_template['Properties']['DatapointsToAlarm'] = alarm['DatapointsToAlarm']

    condition = resource_json.get('Condition')
    if condition != None:
        alarm_template[f'{resource}{alarm["AlarmName"]}']["Condition"] = condition
        return alarm_template
    else:
        return alarm_template
