FROM public.ecr.aws/lambda/python:3.9

COPY app.py requirements/common.txt requirements/prod.txt ./

RUN python3.9 -m pip install -r prod.txt -t .

USER app

# Command can be overwritten by providing a different command in the template directly.
CMD ["app.lambda_handler"]
