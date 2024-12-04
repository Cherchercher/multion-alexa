

Running locally

prereqs:
aws cli &&
docker installed.

docker build -t alexa-multion .
docker run -p 9000:8080 alexa-multion

testing locally

deploy:

docker build -t alexa-multion .
docker tag alexa-multion 439771703274.dkr.ecr.us-east-1.amazonaws.com/alexa-multion:latest
docker push  439771703274.dkr.ecr.us-east-1.amazonaws.com/alexa-multion:latest

curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" \
-H "Content-Type: application/json" \
-d @launch_event.json