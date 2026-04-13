from app.config.settings import get_settings

# --- Non-sensitive constants ---
ROLES = ["owner", "participant"]
DEFAULT_PROJECT_DESCRIPTION = get_settings().default_project_description
MAX_DOCUMENT_UPLOAD_SIZE_MB = 50
ALLOWED_DOCUMENT_EXTENSIONS = ["pdf", "docx", "xlsx"]
