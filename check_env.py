from dotenv import load_dotenv
import os

# Load the .env file
load_dotenv()

# Print all relevant variables
print("POSTGRES_USER =", os.getenv("POSTGRES_USER"))
print("POSTGRES_PASSWORD =", os.getenv("POSTGRES_PASSWORD"))
print("POSTGRES_HOST =", os.getenv("POSTGRES_HOST"))
print("POSTGRES_PORT =", os.getenv("POSTGRES_PORT"))
print("POSTGRES_DB =", os.getenv("POSTGRES_DB"))