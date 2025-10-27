from fastapi.testclient import TestClient
from app.main import app
import os

os.environ.pop("URN_ALLOWED_DOMAINS", None)
os.environ.pop("URN_ALLOWED_OBJ_TYPES", None)
os.environ.pop("URN_CATALOGS_JSON", None)

client = TestClient(app)

# First test: generate
resp = client.post('/api/v1/generate', json={
    'state':'nrw','domain':'bimschg','obj_type':'anlage','local_aktenzeichen':'4711-0815-K1','store': False
})
print("Generate:", resp.status_code, resp.json())

if resp.status_code == 200:
    urn = resp.json()["urn"]
    # Second test: resolve
    r3 = client.get("/api/v1/resolve", params={"urn": urn})
    print("Resolve:", r3.status_code, r3.json() if r3.status_code == 200 else r3.text)
