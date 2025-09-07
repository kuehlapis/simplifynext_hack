# SimplifyNext Hack - Setup Instructions

## Prerequisites

- [Node.js](https://nodejs.org/) (v14.0.0 or later)
- [npm](https://www.npmjs.com/) (v6.0.0 or later) or [Yarn](https://yarnpkg.com/) (v1.22.0 or later)
- A code editor like [Visual Studio Code](https://code.visualstudio.com/)
- Git installed on your machine

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd simplifynext_hack/client
   ```

2. Install the dependencies:
   ```bash
   npm install
   # or
   yarn
   ```

## Configuration

1. Create a `.env.local` file in the root directory of the project with the following environment variables:
   ```
   NEXT_PUBLIC_API_URL=your_api_url_here
   # Add other environment variables as needed
   ```

## Running the Project Locally

1. Start the development server:
   ```bash
   npm run dev
   # or
   yarn dev
   ```

2. Open [http://localhost:3000](http://localhost:3000) in your browser to see the application.

## Building for Production

1. Build the project:
   ```bash
   npm run build
   # or
   yarn build
   ```

2. Start the production server:
   ```bash
   npm start
   # or
   yarn start
   ```

## Project Structure

- `pages/`: Contains all the pages of the application
- `components/`: Reusable React components
- `public/`: Static assets like images and fonts
- `styles/`: CSS or styled-component files
- `utils/`: Utility functions and helpers

## Troubleshooting

### Common Issues

1. **Node.js version issues**: Make sure you're using a compatible Node.js version.
   ```bash
   node --version
   ```

2. **Port already in use**: If port 3000 is already in use, you can specify a different port:
   ```bash
   npm run dev -- -p 3001
   # or
   yarn dev -p 3001
   ```

3. **Dependencies installation failures**: Try removing the node_modules folder and reinstalling:
   ```bash
   rm -rf node_modules
   npm install
   # or
   yarn
   ```

# to install uv
```bash
pip install uv
```

# To run backend
```bash
cd server
uv sync
uv run fastapi dev main.py
```

# .env file
```
GEMINI_API_KEY=your_gemini_api_key_here
GMAIL_ACC=your_gmail_account_here
GMAIL_PW=your_gmail_password_here
```