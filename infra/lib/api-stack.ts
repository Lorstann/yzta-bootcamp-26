import * as path from 'node:path';
import * as cdk from 'aws-cdk-lib/core';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as ecs from 'aws-cdk-lib/aws-ecs';
import * as ecsPatterns from 'aws-cdk-lib/aws-ecs-patterns';
import * as elbv2 from 'aws-cdk-lib/aws-elasticloadbalancingv2';
import * as logs from 'aws-cdk-lib/aws-logs';
import * as rds from 'aws-cdk-lib/aws-rds';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as secretsmanager from 'aws-cdk-lib/aws-secretsmanager';
import { Construct } from 'constructs';

export interface ApiStackProps extends cdk.StackProps {
  readonly vpc: ec2.IVpc;
  readonly cluster: rds.IDatabaseCluster;
  readonly dbSecret: secretsmanager.ISecret;
  readonly jwtSecret: secretsmanager.ISecret;
  readonly llmApiKeySecret: secretsmanager.ISecret;
  readonly uploadsBucket: s3.IBucket;
}

export class ApiStack extends cdk.Stack {
  public readonly loadBalancer: elbv2.ApplicationLoadBalancer;
  public readonly service: ecsPatterns.ApplicationLoadBalancedFargateService;

  constructor(scope: Construct, id: string, props: ApiStackProps) {
    super(scope, id, props);

    const repoRoot = path.join(__dirname, '..', '..');

    this.service = new ecsPatterns.ApplicationLoadBalancedFargateService(this, 'Api', {
      vpc: props.vpc,
      cpu: 512,
      memoryLimitMiB: 1024,
      desiredCount: 1,
      publicLoadBalancer: true,
      assignPublicIp: false,
      listenerPort: 80,
      taskImageOptions: {
        image: ecs.ContainerImage.fromAsset(repoRoot, {
          file: 'backend/Dockerfile',
        }),
        containerName: 'equa-api',
        containerPort: 8000,
        enableLogging: true,
        logDriver: ecs.LogDrivers.awsLogs({
          streamPrefix: 'equa-api',
          logRetention: logs.RetentionDays.ONE_WEEK,
        }),
        environment: {
          APP_ENV: 'production',
          APP_HOST: '0.0.0.0',
          APP_PORT: '8000',
          LOG_LEVEL: 'info',
          DB_HOST: props.cluster.clusterEndpoint.hostname,
          DB_PORT: String(props.cluster.clusterEndpoint.port),
          DB_NAME: 'equa',
          STORAGE_BACKEND: 's3',
          S3_BUCKET: props.uploadsBucket.bucketName,
          S3_REGION: this.region,
          // Same-origin via CloudFront; browser CORS not required for /api
          CORS_ORIGINS: '*',
          LLM_PROVIDER: 'gemini',
          LLM_MODEL: 'gemini-3.5-flash-lite',
          SCOPE_CLASSIFIER_ENABLED: 'true',
        },
        secrets: {
          DB_USER: ecs.Secret.fromSecretsManager(props.dbSecret, 'username'),
          DB_PASSWORD: ecs.Secret.fromSecretsManager(props.dbSecret, 'password'),
          JWT_SECRET: ecs.Secret.fromSecretsManager(props.jwtSecret),
          LLM_API_KEY: ecs.Secret.fromSecretsManager(props.llmApiKeySecret),
        },
      },
      circuitBreaker: { rollback: true },
    });

    this.loadBalancer = this.service.loadBalancer;
    this.loadBalancer.setAttribute('idle_timeout.timeout_seconds', '300');

    this.service.targetGroup.configureHealthCheck({
      path: '/api/v1/health',
      healthyHttpCodes: '200',
      interval: cdk.Duration.seconds(30),
      healthyThresholdCount: 2,
      unhealthyThresholdCount: 3,
    });

    props.uploadsBucket.grantReadWrite(this.service.taskDefinition.taskRole);
    props.jwtSecret.grantRead(this.service.taskDefinition.executionRole!);
    props.llmApiKeySecret.grantRead(this.service.taskDefinition.executionRole!);
    props.dbSecret.grantRead(this.service.taskDefinition.executionRole!);

    new cdk.CfnOutput(this, 'AlbDnsName', {
      value: this.loadBalancer.loadBalancerDnsName,
    });
    new cdk.CfnOutput(this, 'ServiceName', {
      value: this.service.service.serviceName,
    });

    cdk.Tags.of(this).add('Project', 'Equa');
    cdk.Tags.of(this).add('Environment', 'demo');
  }
}
