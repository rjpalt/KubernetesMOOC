FROM mcr.microsoft.com/playwright:v1.55.0-jammy

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy test files
COPY . .

# Default command
CMD ["npx", "playwright", "test"]
