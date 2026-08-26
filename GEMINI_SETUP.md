# Gemini API setup

SevaSetu AI now uses the current Google GenAI Python SDK and `gemini-3.7-flash` for chatbot responses.

1. Keep the Gemini API key on the **backend server only**.
2. Set `GEMINI_API_KEY` in the backend hosting provider environment variables.
3. Set `AI_MODEL=gemini-3.7-flash`.
4. Do not put the key in React frontend variables or commit it to Git.
5. Restart/redeploy the backend after setting the variables.

The React chatbot already calls `POST /api/v1/queries/ask`; that endpoint runs the RAG retrieval and sends the grounded prompt to Gemini.
