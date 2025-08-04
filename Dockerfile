FROM node:18-slim

WORKDIR /app

# Copy package files and install dependencies.
# No external dependencies are needed now, but this is good practice.
COPY package*.json ./
RUN npm install

# Copy the rest of the application code.
COPY . .

# Set the default command to run the script.
CMD ["npm", "start"]
