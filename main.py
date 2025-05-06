from fastapi import FastAPI, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from db import SessionLocal, init_db
from models.ehr_models import (
    BloodPressure,
    BodyTemperature,
    CompositionContext,
    Pulse,
    PulseOximetry,
    Respiration,
)

app = FastAPI()
init_db()

templates = Jinja2Templates(directory="templates")


@app.get("/form/vitals")
def vitals_form(request: Request):
    return templates.TemplateResponse("vitals_form.html", {"request": request})


@app.post("/form/vitals")
def submit_vitals(
    request: Request,
    spo2_numerator: float = Form(...),
    respiration_rate: float = Form(None),
    temperature: float = Form(None),
    body_exposure: str = Form(None),
    location: str = Form(None),
    pulse_rate: float = Form(None),
    pulse_position: str = Form(None),
    pulse_body_site: str = Form(None),
    systolic: float = Form(None),
    diastolic: float = Form(None),
    bp_position: str = Form(None),
    bp_location: str = Form(None),
):
    db = SessionLocal()

    context = CompositionContext()
    db.add(context)
    db.commit()
    db.refresh(context)

    db.add(PulseOximetry(spo2_numerator=spo2_numerator))
    if respiration_rate is not None:
        db.add(Respiration(rate=respiration_rate))
    if temperature is not None:
        db.add(
            BodyTemperature(
                temperature=temperature, body_exposure=body_exposure, location=location
            )
        )
    if pulse_rate is not None:
        db.add(
            Pulse(rate=pulse_rate, position=pulse_position, body_site=pulse_body_site)
        )
    if systolic is not None or diastolic is not None:
        db.add(
            BloodPressure(
                systolic=systolic,
                diastolic=diastolic,
                position=bp_position,
                location=bp_location,
            )
        )

    db.commit()
    db.close()

    return RedirectResponse(url="/form/vitals", status_code=303)
