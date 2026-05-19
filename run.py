import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "backend"))

import uvicorn
from main import app  # noqa: E402

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
