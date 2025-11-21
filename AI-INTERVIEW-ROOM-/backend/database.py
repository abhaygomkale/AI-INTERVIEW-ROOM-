from sqlalchemy import create_engine
from urllib.parse import quote_plus

raw_password = "airoom&2005123"
password = quote_plus(raw_password)

DATABASE_URL = "postgresql://postgres:airoom&2005123@aws-0-xxx.pooler.supabase.co:6543/postgres"


engine = create_engine(DATABASE_URL, pool_pre_ping=True)