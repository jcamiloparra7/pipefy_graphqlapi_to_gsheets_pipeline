aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin "$AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com"
docker build --platform linux/amd64 -t $FUNCTION_NAME ./
docker tag "$FUNCTION_NAME":latest "$AWS_ACCOUNT_ID".dkr.ecr.us-east-1.amazonaws.com/"$FUNCTION_NAME":latest
docker push "$AWS_ACCOUNT_ID".dkr.ecr.us-east-1.amazonaws.com/"$FUNCTION_NAME":latest
aws lambda update-function-code --function-name $FUNCTION_NAME --image-uri "$AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/$FUNCTION_NAME:latest"