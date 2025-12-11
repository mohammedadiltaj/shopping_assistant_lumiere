# 🚀 Free Deployment Guide for Lumière

This guide explains how to host your AI Personal Shopper for **free** using **Vercel** (Frontend) and **Render** (Backend).

## ⚠️ Important Note on Database
Lumière currently uses **SQLite** (`products.db`).
*   **Problem**: On free cloud platforms (like Render/Vercel), the filesystem is *ephemeral*. This means every time you redeploy or the server restarts, **your database will reset** and changes (cart items) will be lost.
*   **Solution for Hackathon**: Ideally, use a free PostgreSQL database (e.g., **Neon.tech** or **Supabase**) instead of SQLite.
*   **For Demo**: Ephemeral SQLite is fine, just know that data won't persist long-term.

---

## Part 1: Backend Hosting (Render.com)

**Render** is great for Python/FastAPI apps.

1.  **Push your code to GitHub**.
2.  Sign up at [render.com](https://render.com).
3.  Click **New +** -> **Web Service**.
4.  Connect your GitHub repo.
5.  **Settings**:
    *   **Root Directory**: `backend` (Important!)
    *   **Runtime**: Python 3
    *   **Build Command**: `pip install -r requirements.txt`
    *   **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6.  **Environment Variables**:
    *   Add `GROQ_API_KEY` (if using real AI).
    *   Add `PYTHON_VERSION`: `3.11.0`
7.  Click **Create Web Service**.
    *   *Result*: You will get a URL like `https://lumiere-backend.onrender.com`. Copy this!

---

## Part 2: Frontend Hosting (Vercel)

**Vercel** is the best place to host React/Vite apps.

1.  Sign up at [vercel.com](https://vercel.com).
2.  Click **Add New...** -> **Project**.
3.  Import your GitHub repo.
4.  **Configure Project**:
    *   **Root Directory**: Click "Edit" and select `frontend`.
    *   **Framework Preset**: Vite (should detect automatically).
    *   **Environment Variables**:
        *   Key: `VITE_API_URL`
        *   Value: `https://lumiere-backend.onrender.com` (The URL you got from Render).
5.  Click **Deploy**.

---

## Part 3: Connecting Them

You need to tell the Frontend where the Backend lives.

1.  **Update `frontend/src/App.tsx`**:
    *   Ensure your API calls use `import.meta.env.VITE_API_URL`.
    *   Currently, it might be hardcoded to `http://localhost:8000`. Use this pattern:
    ```typescript
    const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
    ```
2.  **CORS in Backend**:
    *   In `backend/main.py`, update `allow_origins`.
    *   Change `["*"]` (ok for dev) to your specific Vercel URL for better security, or keep `["*"]` for the hackathon.

---

## 🏁 Summary
1.  **Backend** runs on Render.
2.  **Frontend** runs on Vercel.
3.  **VITE_API_URL** connects them.
