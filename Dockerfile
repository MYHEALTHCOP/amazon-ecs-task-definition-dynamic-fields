# pull official base image
FROM python:3.9

# set working directory
WORKDIR /action


# install python dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt


# add source code
COPY . .

ENTRYPOINT [ "python", "/main.py" ]

