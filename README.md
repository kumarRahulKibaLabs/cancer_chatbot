# Medical Insurance Chatbot

A WebSocket-based chatbot application designed to provide information about Personal Cancer Insurance plans. The chatbot uses LangGraph and OpenAI's GPT-4o model to create a conversational experience for potential customers.

## Features

- Real-time chat via WebSocket connection
- Personalized insurance premium quotes based on age, gender, and cancer type
- Multiple coverage options (Premium, Standard, Basic) for different stages of cancer
- Rate limiting to prevent abuse
- Comprehensive error handling

## Tech Stack

- **Backend**: FastAPI, WebSockets, LangGraph, LangChain
- **AI Model**: OpenAI GPT-4o
- **Data Storage**: Excel file for premium data
- **Deployment**: Uvicorn ASGI server

## Prerequisites

- Python 3.8+
- OpenAI API key

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/kumarRahulKibaLabs/cancer_chatbot.git
   cd cancer_chatbot
   ```

2. Create a virtual environment:
   ```
   python -m venv myenv
   source myenv/bin/activate  # On Windows: myenv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

## Project Structure

```
cancer_chatbot/
├── chatbot/
│   ├── __init__.py
│   ├── graph.py         # LangGraph workflow setup
│   ├── prompt.py        # System prompts for the chatbot
│   ├── tools.py         # Tool definitions for premium calculation
│   └── websocket.py     # WebSocket handler
├── premium.xlsx         # Premium data for different cancer types
├── main.py              # FastAPI application entry point
├── requirements.txt     # Project dependencies
└── README.md            # Project documentation
```

## Usage

1. Start the server:
   ```
   python main.py
   ```

2. The server will start on `http://0.0.0.0:8000` by default.

3. Connect to the WebSocket endpoint at `ws://localhost:8000/chat` from your frontend application.

4. Send messages to the chatbot and receive responses in real-time.

## API Endpoints

- `GET /`: Welcome message and information about the WebSocket endpoint
- `WebSocket /chat`: Main chat endpoint for real-time communication with the chatbot

## Premium Data

The chatbot uses an Excel file (`premium.xlsx`) to retrieve premium information based on:

- Age groups (15-20, 20-25, 25-30, 30-35, 35-40, 40-45, 45-50, 50-55)
- Gender (Male, Female)
- Cancer types (Kidney, Lung, Throat, Skin, Thyroid, Cervical, Bone, Bladder)
- Cancer stages (Early, Major, Advanced)
- Coverage options (Premium, Standard, Basic)

## Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `HOST`: Host to bind the server to (default: 0.0.0.0)
- `PORT`: Port to run the server on (default: 8000)

## Rate Limiting

The application implements a rate limit of 100 connections per hour per IP address to prevent abuse.

## Error Handling

The application includes comprehensive error handling for:
- WebSocket disconnections
- Invalid input parameters
- Missing premium data
- API errors

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.