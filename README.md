# Dark Fantasy Book Generator

This project is a web application that generates dark fantasy books using AI.

## Project Structure

- `frontend/`: Contains the React frontend application.
- `backend/`: Contains the FastAPI backend application and the book generation logic.

## How to Run

### Prerequisites

- Node.js and npm
- Python 3.7+ and pip

### Backend

1.  Navigate to the `backend` directory:
    ```bash
    cd backend
    ```

2.  Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

3.  Create a `.env` file in the `backend` directory and add your Google API key:
    ```
    GOOGLE_API_KEY=your_api_key
    ```

4.  Start the backend server:
    ```bash
    uvicorn main:app --reload
    ```
    The backend server will be running on `http://localhost:8000`.

### Frontend

1.  Navigate to the `frontend` directory:
    ```bash
    cd frontend
    ```

2.  Install the required npm packages:
    ```bash
    npm install
    ```

3.  Start the frontend development server:
    ```bash
    npm start
    ```
    The frontend application will be running on `http://localhost:3000`.

4.  Open your browser and go to `http://localhost:3000` to use the application.
