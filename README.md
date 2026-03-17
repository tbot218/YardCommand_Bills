# YardCommand

YardCommand is a bills calendar app with a neon HUD interface, built with:

- FastAPI backend
- React frontend
- Render-ready deployment config

## Local development

Backend:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --reload
```

Frontend:

```powershell
cd .\yardcommand-ui
npm start
```

## GitHub setup

Initialize the repo locally:

```powershell
git init
git add .
git commit -m "Initial YardCommand bills calendar"
```

Connect your GitHub repo:

```powershell
git remote add origin <YOUR_GITHUB_REPO_URL>
git branch -M main
git push -u origin main
```

## Render deployment

This repo includes [render.yaml](C:\Users\cassi\PycharmProjects\PythonProject\YardCommand\render.yaml) for:

- `yardcommand-api` as a Python web service
- `yardcommand-ui` as a static site

### Important Render settings

- Set `DATABASE_URL` on the backend service to your Render Postgres database URL.
- Set `REACT_APP_API_BASE_URL` on the frontend service to your backend Render URL if it differs from the placeholder.

## Notes

- Local SQLite files are ignored from git.
- Render should use Postgres instead of SQLite for persistent production data.
