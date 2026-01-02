FROM node:22-alpine

WORKDIR /app

# Install dependencies first (better caching)
COPY package.json package-lock.json ./
RUN npm install

# Copy rest of the frontend
COPY . .

# Next.js / Vite / React dev server
EXPOSE 3000

CMD ["npm", "run", "dev"]
