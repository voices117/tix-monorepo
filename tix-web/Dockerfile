FROM node:6.9.0

RUN npm install --global yarn

COPY ./package.json /app/
COPY ./yarn.lock /app/

WORKDIR /app

RUN yarn install

COPY . /app

RUN npm run compile
CMD ["npm", "run", "dev"]
