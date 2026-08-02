import * as cdk from 'aws-cdk-lib/core';
import { Template } from 'aws-cdk-lib/assertions';
import { NetworkStack } from '../lib/network-stack';

test('NetworkStack creates a VPC', () => {
  const app = new cdk.App();
  const stack = new NetworkStack(app, 'TestNetwork');
  const template = Template.fromStack(stack);
  template.resourceCountIs('AWS::EC2::VPC', 1);
});
