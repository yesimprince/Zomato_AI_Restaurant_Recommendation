# Deployment Plan

This document outlines the step-by-step plan to deploy the Zomato AI Restaurant Recommendation project, with the **Frontend on Vercel** and the **Backend on Railway**.

## 1. Backend Deployment (Railway)

The backend is a FastAPI application in the `src/` directory.

### Prerequisites (Code Changes Required)
Before deploying to Railway, we need to make a few adjustments to the backend code to ensure it runs correctly in a cloud environment:

1. **Update `requirements.txt`**: Add missing dependencies for the web server.
   ```text
   fastapi
   uvicorn
   ```
2. **Update `src/main.py`**: Railway injects a dynamic `PORT` environment variable. The server must listen on `0.0.0.0` and the assigned port.
   ```python
   import os
   
   # In main():
   port = int(os.environ.get("PORT", 8000))
   uvicorn.run(
       "src.api.routes:app",
       host="0.0.0.0",
       port=port,
   )
   ```
3. **Add a `Procfile` (Optional but recommended)**: Create a `Procfile` in the root directory to tell Railway exactly how to start the app:
   ```text
   web: uvicorn src.api.routes:app --host 0.0.0.0 --port $PORT
   ```

### Railway Deployment Steps
1. Go to [Railway.app](https://railway.app/) and log in with your GitHub account.
2. Click **New Project** -> **Deploy from GitHub repo**.
3. Select the `Zomato_AI_Restaurant_Recommendation` repository.
4. **Configure Environment Variables**:
   - Go to the **Variables** tab for your backend service in Railway.
   - Add your `GROQ_API_KEY` and any other variables present in your local `.env`.
5. Railway will automatically detect the Python environment from `requirements.txt` and start the server.
6. Once deployed, Railway will provide a public URL (e.g., `https://your-app.up.railway.app`). Copy this URL; you will need it for the frontend.

---

## 2. Frontend Deployment (Vercel)

The frontend is a static site located in the `frontend/` directory.

### Prerequisites (Code Changes Required)
1. **Update API URL in Frontend**: Ensure your frontend code (e.g., `frontend/app.js`) points to the production Railway URL instead of `http://127.0.0.1:8000`. You can hardcode this or set up an environment variable mechanism if your frontend supports it.

### Vercel Deployment Steps
1. Go to [Vercel.com](https://vercel.com/) and log in with your GitHub account.
2. Click **Add New** -> **Project**.
3. Import the `Zomato_AI_Restaurant_Recommendation` repository.
4. **Configure the Project**:
   - **Framework Preset**: Vercel will likely detect "Other" since it's vanilla HTML/JS/CSS.
   - **Root Directory**: Click "Edit" and select the `frontend` folder.
   - **Build Command**: Leave blank (or use the default if it detects one).
   - **Output Directory**: Leave blank.
5. Click **Deploy**. Vercel will serve your `index.html` file and static assets immediately.
6. Vercel will provide a public URL for your frontend (e.g., `https://zomato-ai.vercel.app`).

---

## 3. Post-Deployment Verification
- Ensure the frontend can successfully communicate with the backend. Check the browser console and network tab to verify API requests to the Railway URL are returning HTTP 200 statuses without CORS errors.
- **CORS Setup**: Make sure the FastAPI backend (`src/api/routes.py`) has `CORSMiddleware` configured to allow requests from the Vercel frontend URL.
