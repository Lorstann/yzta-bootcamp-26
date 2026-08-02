#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib/core';
import { NetworkStack } from '../lib/network-stack';
import { DataStack } from '../lib/data-stack';
import { ApiStack } from '../lib/api-stack';
import { FrontendStack } from '../lib/frontend-stack';

const app = new cdk.App();

const env: cdk.Environment = {
  account: process.env.CDK_DEFAULT_ACCOUNT,
  region: process.env.CDK_DEFAULT_REGION ?? 'us-east-1',
};

const network = new NetworkStack(app, 'EquaNetwork', { env });

const data = new DataStack(app, 'EquaData', {
  env,
  vpc: network.vpc,
});

const api = new ApiStack(app, 'EquaApi', {
  env,
  vpc: network.vpc,
  cluster: data.cluster,
  dbSecret: data.cluster.secret!,
  jwtSecret: data.jwtSecret,
  llmApiKeySecret: data.llmApiKeySecret,
  uploadsBucket: data.uploadsBucket,
});

new FrontendStack(app, 'EquaFrontend', {
  env,
  loadBalancer: api.loadBalancer,
});

app.synth();
