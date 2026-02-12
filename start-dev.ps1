# Start Backend
Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", "cd backend; .\.venv\Scripts\Activate.ps1; python -m uvicorn app.main:app --reload --port 8000"

# Start Frontend
Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", "cd frontend; pnpm dev"
