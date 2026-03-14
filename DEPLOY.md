# Deploy AI Image Analyzer on Render

This app runs as **two Web Services** on Render: a FastAPI backend (API) and a Streamlit frontend (UI). Both use the same repository and `requirements.txt`; only the start command and environment variables differ. The UI calls the API at the URL you set via `API_URL`.

---

## Prerequisites

- A **Git repository** (GitHub or GitLab) containing the app (`app/`, `ui/`, `requirements.txt`, and optionally `render.yaml`).
- A **Render account** at [render.com](https://render.com).

---

## Two services overview

| Service | Role | Start command |
|--------|------|----------------|
| **Backend (API)** | FastAPI; handles image upload, cache, and LLM calls | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| **Frontend (UI)** | Streamlit; upload UI and display results | `streamlit run ui/streamlit_app.py --server.port $PORT --server.address 0.0.0.0` |

Render sets `$PORT` (default 10000) for each service. The frontend must have **`API_URL`** set to the backend’s public URL (e.g. `https://ai-image-analyzer-api.onrender.com`). When using the Blueprint (`render.yaml`), this is done automatically via `fromService`.

---

## Option A: Deploy with Blueprint (automated)

1. Push **`render.yaml`** to your repo (it should be in the repo root or the same root as `requirements.txt`).

2. In the **Render Dashboard**: click **New > Blueprint**.

3. Connect your Git provider and select the repository that contains `render.yaml`.

4. Render will detect the Blueprint and show the two services. Confirm and apply. When prompted, enter **secret environment variables** for the **backend** service:
   - **OPENAI_API_KEY** (required if using GPT models), and/or  
   - **GEMINI_API_KEY**, **ANTHROPIC_API_KEY** if you use those providers.

5. Deploy. After both services finish building and starting:
   - Backend URL: `https://ai-image-analyzer-api.onrender.com` (or the name you gave in `render.yaml`).
   - Frontend URL: `https://ai-image-analyzer-ui.onrender.com`. The UI already has `API_URL` set from the backend’s `RENDER_EXTERNAL_URL`.

6. Optional: In the Dashboard, add or change **AI_MODEL** and other backend env vars (e.g. `CACHE_BACKEND`, `MAX_IMAGE_DIMENSION`) on the **backend** service.

---

## Option B: Deploy manually (two Web Services)

### Backend (API)

1. **New > Web Service**; connect your repo.
2. If the app lives in a subfolder (e.g. `AI_IMAGE_ANALYZER`), set **Root Directory** to that folder.
3. **Build command:** `pip install -r requirements.txt`
4. **Start command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. **Environment variables** (in Dashboard):
   - `AI_MODEL` = `gpt-4o` (or your model)
   - `OPENAI_API_KEY` = (your key) — or `GEMINI_API_KEY` / `ANTHROPIC_API_KEY` as needed
   - `CACHE_BACKEND` = `file`
   - `CACHE_FILE_PATH` = `image_cache.json`
6. Create the service and deploy. Copy the service URL (e.g. `https://ai-image-analyzer-api.onrender.com`).

### Frontend (UI)

1. **New > Web Service**; same repo (and same **Root Directory** if used).
2. **Build command:** `pip install -r requirements.txt`
3. **Start command:** `streamlit run ui/streamlit_app.py --server.port $PORT --server.address 0.0.0.0`
4. **Environment variable:** `API_URL` = backend URL from above (e.g. `https://ai-image-analyzer-api.onrender.com`). No trailing slash.
5. Create the service and deploy. Open the frontend URL to use the app.

---

## Environment variables reference

### Backend (API)

| Variable | Description | Example |
|----------|-------------|---------|
| `AI_MODEL` | Vision model name | `gpt-4o`, `gemini-2.0-flash` |
| `OPENAI_API_KEY` | OpenAI API key (for GPT) | (secret) |
| `GEMINI_API_KEY` | Google Gemini API key | (secret) |
| `ANTHROPIC_API_KEY` | Anthropic API key (for Claude) | (secret) |
| `CACHE_BACKEND` | `file` or `diskcache` | `file` |
| `CACHE_FILE_PATH` | Path for file cache | `image_cache.json` |
| `MAX_IMAGE_DIMENSION` | Max image side after resize | `2048` |
| `JPEG_QUALITY` | JPEG quality for normalization | `85` |

Do **not** set `PORT`; Render sets it automatically.

### Frontend (UI)

| Variable | Description | Example |
|----------|-------------|---------|
| `API_URL` | Backend’s public URL | `https://ai-image-analyzer-api.onrender.com` |

When using the Blueprint, `API_URL` is set automatically from the backend service’s `RENDER_EXTERNAL_URL`.

---

## Cold starts and free tier

On the **free tier**, Render spins down services after a period of inactivity. The first request after a spin-down can take **30–60+ seconds** (cold start). Both the API and the UI can spin down; wake the backend first (e.g. open the API URL or trigger the UI), then use the app. Consider a paid plan if you need always-on or faster response.

---

## Troubleshooting

- **UI shows “Cannot reach analyzer service”**  
  - Ensure **API_URL** on the frontend is exactly the backend’s URL (with `https://`, no trailing slash).  
  - Ensure the backend service is deployed and running (check its logs and URL in the Dashboard).

- **Backend fails to start**  
  - Check **Build logs** for `pip install` errors; ensure `requirements.txt` includes `fastapi`, `uvicorn[standard]`, `litellm`, etc.  
  - If the repo root is a parent folder, set **Root Directory** to the folder that contains `app/` and `requirements.txt`.

- **Streamlit not binding / service unreachable**  
  - Start command must include `--server.port $PORT` and `--server.address 0.0.0.0`.

- **Blueprint: API_URL not set on frontend**  
  - Confirm the **backend** service name in `render.yaml` matches the actual service name (e.g. `ai-image-analyzer-api`).  
  - After the first deploy, `RENDER_EXTERNAL_URL` is set on the backend; the frontend’s `fromService` will use it on the next deploy or manual sync.

---

## Summary

- **Blueprint:** Use `render.yaml` and **New > Blueprint** for one-time setup of both services and linked `API_URL`.
- **Manual:** Create two Web Services, same repo, same build command; different start commands and env vars; set `API_URL` on the UI to the API’s URL.
- **Secrets:** Set API keys in the Render Dashboard (never commit them). Use `sync: false` in the Blueprint for keys so Render prompts you.
