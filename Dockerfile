# Use an official Node.js runtime as the base image
FROM node:21

# Set the working directory in the container to /app
WORKDIR /app

# Copy package.json and package-lock.json to the working directory
COPY backend/package*.json ./

# Install any needed packages specified in package.json
RUN npm install

# Bundle app source inside Docker image
COPY backend .

# Make port 3000 available to the world outside this container
EXPOSE 3000

# Define the command to run your app using CMD which defines your runtime
# Here we use the npm start command to start your server
CMD [ "npm", "start" ]