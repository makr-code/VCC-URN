from fastapi.testclient import TestClient
from app.main import app
client = TestClient(app)
resp = client.post('/api/v1/generate', json={
    'state':'nrw','domain':'bimschg','obj_type':'anlage','local_aktenzeichen':'4711-0815-K1','store': False
})
print(resp.status_code, resp.json())
