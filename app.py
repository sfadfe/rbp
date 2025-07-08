from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

latest = {"distance": None, "error": None}

@app.get("/")
def main_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/sensor")
async def receive_distance(req: Request):
    raw = await req.body()
    text = raw.decode('utf-8', errors='ignore')
    print(" Raw body   :", repr(text))
    print(" Content-Type:", req.headers.get('content-type'))
    try:
        data = json.loads(text)
    except Exception as e:
        print("JSON 디코드 에러:", e)
        return {"status":"error","detail":"invalid json","raw":text}
    print("▶ 파싱된 data:", data)
    latest["distance"] = data.get("distance")
    return {"status":"ok","distance":latest["distance"]}



@app.get("/sensor")
async def send_distance():
    return latest

