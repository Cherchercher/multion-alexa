# Amazon Shop Assistant

Perform actions on Amazon.com by voice commands. For example, to place an order, get gift ideas suggestions, and tracking orders.

Powered by Alexa Skills and Multon.ai.

---

# Running Locally

## Prerequisites
Ensure the following are installed on your machine:
- [AWS CLI](https://aws.amazon.com/cli/)
- [Docker](https://www.docker.com/)

---

## Testing Locally

1. Run the Docker container:
   ```
   docker run -p 9000:8080 multion-amazon
   ```
2. Run test events:

   ```
   curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" \
   -H "Content-Type: application/json" \
   -d @launch_event.json
   ```

## Deployment

1. Login to aws
```
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
```

2. Build, tag, and push the docker image
```
export $(cat .env | xargs)  # Export the variables from .env file
docker build -t multion-amazon . --no-cache \
  --build-arg AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION \
  --build-arg MULTION_API_KEY=$MULTION_API_KEY \
  --build-arg OPENAI_API_KEY=$OPENAI_API_KEY \

docker tag multion-amazon $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/multion-amazon:tag
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/multion-amazon:tag
```

3. Update your lambda function
aws lambda update-function-code \
           --function-name multion-amazon-docker \
           --image-uri $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/multion-amazon:tag


