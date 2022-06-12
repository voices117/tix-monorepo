FROM node:boron

ENV DEBIAN_FRONTEND=noninteractive
RUN apt update && apt install -y python-pip && rm -rf /var/lib/apt/lists/*
RUN pip install MySQL-python

# Create app directory
WORKDIR /usr/src/app

# Install app dependencies
COPY package.json .
RUN npm install

# Bundle app source
COPY . .

EXPOSE 3001

CMD ["npm", "start"]
