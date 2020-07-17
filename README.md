# cloudwatch-serverless-alarm-macro
Now Supports CloudFormation Conditions

CloudFormation Macro that will append a set of CloudWatch alarms for supported resources.

## Included alarms
Lambda, and Dynamo DB

|Service | Alarm   | Description  |
|---|---|---|
|Lambda  |  Errors | The number of invocations that failed due to errors in the function (response code 4XX)  |
|Dynamo DB |  ConsumedReadCapacityUnits | When 80% of read capacity units have been reached (Works only on provisioned throughput)  |
|Dynamo DB  | ConsumedWriteCapacityUnits  |  When 80% of write capacity units have been reached (Works only on provisioned throughput) |

## Installation
Clone the git repo
Use the AWS CLI to set the appropriate profile/API keys. Open a terminal, and from the root of the repository directory, 
type the following, replacing $BUCKET and $STACKNAME with your own values.

```
aws cloudformation package --template-file ServerlessAlarmsMacro.yaml --s3-bucket $BUCKET  --output-template-file packaged-template.yaml

aws cloudformation deploy --template-file packaged-template.yaml --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND --stack-name $STACKNAME 
```

## Usage

To use the macro, add the following line to the top of your templates:
```yaml
Transform: ServerlessAlarmMacro
```

## Macro Order for Serverless Templates

If you are deploying a serverless template please ensure you list this macro after the serverless transform
```yaml
Transform: ["AWS::Serverless-2016-10-31", "AlarmMacro"]
```

## Required Params

Since you are more than likely going to be publishing alarms to an SNS topic, 
the following parameter is required in your template.

```yaml
    AlarmsSNSArn:
        Type: String
        Description: Name for alarms sns topic
        Default: 'arn:aws:sns:<region>:<account>:<topic name>'
```

You can change this by passing it into your cloudformation changeset creation 
if you want to have different topics for different stages.

## Future Work
I will progressively start adding more types of resources and allow a configureable template

## Honourable Mentions
My initial template was based off of the AWS supplied macro 
[AlarmsMacro](https://aws.amazon.com/blogs/infrastructure-and-automation/automating-amazon-cloudwatch-alarms-with-an-aws-cloudformation-macro/)
 and some additional knowledge from learned from [SAR-cloudwatch-alarms-macro](https://github.com/lumigo/SAR-cloudwatch-alarms-macro)