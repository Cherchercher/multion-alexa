# OpenTable Voice Assistant

Perform actions on OpenTable.com by voice commands. For example, to make, change, or cancel a reservation. 

Save your personal preferences for your next reservation. 

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
   docker run -p 9000:8080 multion-opentable
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
docker build -t multion-opentable . --no-cache \
  --build-arg AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION \
  --build-arg MULTION_API_KEY=$MULTION_API_KEY \
  --build-arg OPENAI_API_KEY=$OPENAI_API_KEY \
  --build-arg MEM0_API_KEY=$MEM0_API_KEY

docker tag multion-opentable $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/multion-opentable:tag
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/multion-opentable:tag
```

3. Update your lambda function
aws lambda update-function-code \
           --function-name multion-opentable-docker \
           --image-uri $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/multion-opentable:tag


