-- DOCUMENTS
CREATE INDEX idx_documents_project_id ON documents(project_id);

-- PROJECT_USERS (critical)
CREATE INDEX idx_pu_user_id ON project_users(user_id);
CREATE INDEX idx_pu_project_id ON project_users(project_id);
CREATE INDEX idx_pu_role_id ON project_users(role_id);