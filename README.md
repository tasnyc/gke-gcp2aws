# gke-gcp2aws

Connect from a GKE Pod to AWS

## Description

This is a Docker image that runs on GKE that can be used to test connectivity to AWS using Google Service Account Unique ID in a AWS Role  Trusted Relationships using AssumeRoleWithWebIdentity. Once connectivity is confirmed you can test scripts as needed to make sure everythin is working as expected. For example maybe you want to pull in some objects from an AWS S3 bucket and parse some info from those objects.

Docker image is hosted in [Docker Hub](https://hub.docker.com/repository/docker/tasnyc/gke2aws-image/general).

## Getting Started

### Dependencies

* GCP Project
  * GCP Service Account (GSA)
  * GKE Cluster
* GCP Workload Identity Knowledge - [Link](https://cloud.google.com/kubernetes-engine/docs/how-to/workload-identity)  
* AWS Account
  * AWS Role

### Configuration

* Create a Google Service Account and get the `Unique ID` of that GSA.
  *  Add roles/iam.workloadIdentityUser to the created GSA and link it to namespace/KSA (Kubernetes Service account) example : [my-namespace/my-ksa].
* Create a AWS role with Trusted Relationships using AssumeRoleWithWebIdentity and whatever permissions you want to be able to do on the AWS side.

Example Role to be able to list/get objects in S3 bucket.
Trusted Relationships (assume role):
```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Federated": "accounts.google.com"
            },
            "Action": "sts:AssumeRoleWithWebIdentity",
            "Condition": {
                "StringEquals": {
                    "accounts.google.com:aud": "1234567890123456789"
                }
            }
        }
    ]
}
```
That Id is the Unique ID of that GSA you created on GCP.

Permissions to S3 called testbucket 
```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": [
                "s3:GetObject"
            ],
            "Effect": "Allow",
            "Resource": [
                "arn:aws:s3:::testbucket/*"
            ]
        },
        {
            "Action": [
                "s3:ListBucket"
            ],
            "Effect": "Allow",
            "Resource": [
                "arn:aws:s3:::testbucket"
            ]
        }
    ]
}
```
On the GKE side once you get a shell into the pod ( instructions below) modify (using vim) the /app/.aws/credentials file subtituting the `arn:aws:iam::123456789:role/myawsrole` Role ARN with the actual ARN of the role you created above. 

### Setup

* Start the pod and get a shell in the container to run some tests. Pod gets deleted on exit. 
```
kubectl run -it --rm -n my-namespace --image tasnyc/gke2aws-image:latest --overrides='{ "spec": { "serviceAccount": "my-ksa" }}' gcp2aws --command sh
```
OR
* Start the pod which would continuously run, letting you shell into the container whenever you want to to run tests.
Run POD:
```
kubectl run -n my-namespace --image tasnyc/gke2aws-image:latest --overrides='{ "spec": { "serviceAccount": "my-ksa" }}' gcp2aws2-pod
```
Get a shell into the container:
```
kubectl exec -it -n my-namespace gcp2aws2-pod -c gcp2aws2 -- sh
```
Once done with the Pod and no longer need it, delete it:
```
kubectl -n my-namespace delete pod gcp2aws2-pod
```
## Executing
Once all above is completed and you made the change to the /app/.aws/credentials file with your role ARN you should be able to run this. 
```
aws --profile GCPAWS s3 ls s3://testbucket --recursive
```
Example Ouput:
List Buckets in AWS Account
```
$ aws --profile GCPAWS s3 ls s3://
2021-02-03 18:39:19 s3-bucket-1
2020-08-12 17:50:52 s3-bucket-2
2020-12-16 20:21:54 s3-bucket-3
2023-09-26 16:34:56 testbucket
```
List objects in the testbucket S3 bucket:
```
$ aws --profile GCPAWS s3 ls s3://testbucket --recursive
2023-09-05 14:20:40          0 archive/Folder/
2023-09-13 15:31:11        999 archive/Folder/2023-06-29.csv
2023-09-13 15:31:12        999 archive/Folder/2023-06-30.csv
2023-09-13 15:31:12       7015 archive/Folder/2023-07-01.csv
2023-09-13 15:31:12       3541 archive/Folder/2023-08-03.csv
2023-09-13 15:31:12        999 archive/Folder/export_test.csv
```


## Authors

tasnyc   

## Version History

* 0.1
    * Initial Release
