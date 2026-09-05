"""Навчальний застосунок: показує середовище, у якому його запущено."""
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

import envinfo

app = FastAPI(title="Паспорт середовища")


@app.get("/", response_class=HTMLResponse)
def page(request: Request) -> str:
    return envinfo.render_page(envinfo.collect(), envinfo.request_facts(request))


@app.get("/api/env")
def environment(request: Request) -> dict:
    return {"environment": envinfo.collect(), "request": envinfo.request_facts(request)}


@app.get("/healthz")
def healthz() -> dict:
    return {"status": "ok"}
