#!/usr/bin/env bash

S3_BUCKET=$1

cd $PWD/pipeline/lambda_functions/zipped_lambdas/

for f in *.zip; do
    aws s3 cp $f s3://$S3_BUCKET
    echo 'uploaded '$f
 done
