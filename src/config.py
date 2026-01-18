import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
    MODEL_ID = os.getenv("MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0")
    PDF_PATH = os.getenv("PDF_PATH", "data/kb_summa_rh.pdf")
    EXCEL_PATH = os.getenv("EXCEL_PATH", "data/cesancias_causadas.xlsx")
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"