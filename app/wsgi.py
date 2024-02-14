import os
import sys

from app import app

if __name__ == "__main__":
  port=(os.environ["PORT"] if "PORT" in os.environ else None) or (sys.argv[1] if len(sys.argv)>1 and sys.argv[1].isdigit() else None) or "8080"
  app.run(port=int(port))
