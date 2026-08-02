import * as cdk from 'aws-cdk-lib/core';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as rds from 'aws-cdk-lib/aws-rds';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as secretsmanager from 'aws-cdk-lib/aws-secretsmanager';
import { Construct } from 'constructs';

export interface DataStackProps extends cdk.StackProps {
  readonly vpc: ec2.IVpc;
}

export class DataStack extends cdk.Stack {
  public readonly cluster: rds.DatabaseCluster;
  public readonly uploadsBucket: s3.Bucket;
  public readonly jwtSecret: secretsmanager.Secret;
  public readonly llmApiKeySecret: secretsmanager.Secret;

  constructor(scope: Construct, id: string, props: DataStackProps) {
    super(scope, id, props);

    this.jwtSecret = new secretsmanager.Secret(this, 'JwtSecret', {
      description: 'Equa JWT signing secret (demo)',
      generateSecretString: {
        passwordLength: 48,
        excludePunctuation: true,
      },
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    // Replace after deploy: aws secretsmanager put-secret-value --secret-id <arn> --secret-string '...'
    this.llmApiKeySecret = new secretsmanager.Secret(this, 'LlmApiKey', {
      description: 'Equa LLM_API_KEY (set value after deploy)',
      secretStringValue: cdk.SecretValue.unsafePlainText('REPLACE_ME'),
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    this.uploadsBucket = new s3.Bucket(this, 'Uploads', {
      encryption: s3.BucketEncryption.S3_MANAGED,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      enforceSSL: true,
      autoDeleteObjects: true,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    const dbSecurityGroup = new ec2.SecurityGroup(this, 'DbSg', {
      vpc: props.vpc,
      description: 'Aurora access from Equa API tasks',
      allowAllOutbound: true,
    });

    this.cluster = new rds.DatabaseCluster(this, 'Aurora', {
      engine: rds.DatabaseClusterEngine.auroraPostgres({
        version: rds.AuroraPostgresEngineVersion.VER_16_8,
      }),
      credentials: rds.Credentials.fromGeneratedSecret('equa'),
      defaultDatabaseName: 'equa',
      writer: rds.ClusterInstance.serverlessV2('Writer', {
        publiclyAccessible: false,
      }),
      serverlessV2MinCapacity: 0.5,
      serverlessV2MaxCapacity: 2,
      vpc: props.vpc,
      vpcSubnets: { subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS },
      securityGroups: [dbSecurityGroup],
      storageEncrypted: true,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      deletionProtection: false,
      enableDataApi: false,
    });

    // Avoid cross-stack SG cycles: allow private VPC CIDR to Postgres.
    this.cluster.connections.allowDefaultPortFrom(
      ec2.Peer.ipv4(props.vpc.vpcCidrBlock),
      'Private VPC to Aurora',
    );
    new cdk.CfnOutput(this, 'JwtSecretArn', {
      value: this.jwtSecret.secretArn,
    });
    new cdk.CfnOutput(this, 'LlmApiKeySecretArn', {
      value: this.llmApiKeySecret.secretArn,
    });
    new cdk.CfnOutput(this, 'UploadsBucketName', {
      value: this.uploadsBucket.bucketName,
    });
    new cdk.CfnOutput(this, 'ClusterEndpoint', {
      value: this.cluster.clusterEndpoint.hostname,
    });

    cdk.Tags.of(this).add('Project', 'Equa');
    cdk.Tags.of(this).add('Environment', 'demo');
  }

}
