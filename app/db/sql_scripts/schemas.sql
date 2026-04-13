-- USERS
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    login VARCHAR NOT NULL UNIQUE,
    email VARCHAR NOT NULL UNIQUE,
    hashed_password VARCHAR NOT NULL
);

-- PROJECTS
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    description TEXT
);

-- ROLES
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL UNIQUE
);

-- DOCUMENTS
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    s3_path VARCHAR NOT NULL,
    project_id INTEGER NOT NULL,
    CONSTRAINT fk_documents_project
        FOREIGN KEY (project_id)
        REFERENCES projects(id)
        ON DELETE CASCADE
);

-- PROJECT_USERS (association table)
CREATE TABLE project_users (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    project_id INTEGER NOT NULL,
    role_id INTEGER NOT NULL,

    CONSTRAINT fk_pu_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_pu_project
        FOREIGN KEY (project_id)
        REFERENCES projects(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_pu_role
        FOREIGN KEY (role_id)
        REFERENCES roles(id),

    CONSTRAINT uix_user_project_role
        UNIQUE (user_id, project_id, role_id)
);