import json
import os
from datetime import date

from fastapi import FastAPI, Form, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from db import SessionLocal, init_db
from models.ehr_models import (
    EHR,
    BloodPressure,
    BodyTemperature,
    Composition,
    CompositionContext,
    Patient,
    Pulse,
    PulseOximetry,
    Respiration,
)

app = FastAPI()
init_db()

templates = Jinja2Templates(directory="templates")


@app.get("/export/fhir")
def export_fhir():
    db = SessionLocal()
    patient = db.query(Patient).first()

    if not patient or not patient.ehr or not patient.ehr.compositions:
        db.close()
        return JSONResponse(content={"error": "No data available"}, status_code=404)

    observations = []

    fhir_patient = {
        "resourceType": "Patient",
        "id": f"{patient.id}",
        "name": [{"text": patient.name}],
        "birthDate": patient.birth_date.isoformat(),
    }

    for composition in patient.ehr.compositions:
        for pulse in composition.pulse:
            observations.append(
                {
                    "resourceType": "Observation",
                    "id": f"obs-pulse-{pulse.id}",
                    "status": "final",
                    "code": {
                        "coding": [
                            {
                                "system": "http://loinc.org",
                                "code": "8867-4",
                                "display": "Heart rate",
                            }
                        ],
                        "text": "Heart Rate",
                    },
                    "subject": {"reference": f"Patient/{patient.id}"},
                    "effectiveDateTime": pulse.timestamp.isoformat(),
                    "valueQuantity": {
                        "value": pulse.rate,
                        "unit": "beats/minute",
                        "system": "http://unitsofmeasure.org",
                        "code": "/min",
                    },
                }
            )

        for bp in composition.blood_pressure:
            if bp.systolic:
                observations.append(
                    {
                        "resourceType": "Observation",
                        "id": f"obs-sbp-{bp.id}",
                        "status": "final",
                        "code": {
                            "coding": [
                                {
                                    "system": "http://loinc.org",
                                    "code": "8480-6",
                                    "display": "Systolic blood pressure",
                                }
                            ],
                            "text": "Systolic BP",
                        },
                        "subject": {"reference": f"Patient/{patient.id}"},
                        "effectiveDateTime": bp.timestamp.isoformat(),
                        "valueQuantity": {
                            "value": bp.systolic,
                            "unit": "mmHg",
                            "system": "http://unitsofmeasure.org",
                            "code": "mm[Hg]",
                        },
                    }
                )
            if bp.diastolic:
                observations.append(
                    {
                        "resourceType": "Observation",
                        "id": f"obs-dbp-{bp.id}",
                        "status": "final",
                        "code": {
                            "coding": [
                                {
                                    "system": "http://loinc.org",
                                    "code": "8462-4",
                                    "display": "Diastolic blood pressure",
                                }
                            ],
                            "text": "Diastolic BP",
                        },
                        "subject": {"reference": f"Patient/{patient.id}"},
                        "effectiveDateTime": bp.timestamp.isoformat(),
                        "valueQuantity": {
                            "value": bp.diastolic,
                            "unit": "mmHg",
                            "system": "http://unitsofmeasure.org",
                            "code": "mm[Hg]",
                        },
                    }
                )

        for temp in composition.body_temperature:
            observations.append(
                {
                    "resourceType": "Observation",
                    "id": f"obs-temp-{temp.id}",
                    "status": "final",
                    "code": {
                        "coding": [
                            {
                                "system": "http://loinc.org",
                                "code": "8310-5",
                                "display": "Body temperature",
                            }
                        ],
                        "text": "Body Temperature",
                    },
                    "subject": {"reference": f"Patient/{patient.id}"},
                    "effectiveDateTime": temp.timestamp.isoformat(),
                    "valueQuantity": {
                        "value": temp.temperature,
                        "unit": "°C",
                        "system": "http://unitsofmeasure.org",
                        "code": "Cel",
                    },
                }
            )

        for resp in composition.respiration:
            observations.append(
                {
                    "resourceType": "Observation",
                    "id": f"obs-resp-{resp.id}",
                    "status": "final",
                    "code": {
                        "coding": [
                            {
                                "system": "http://loinc.org",
                                "code": "9279-1",
                                "display": "Respiratory rate",
                            }
                        ],
                        "text": "Respiratory Rate",
                    },
                    "subject": {"reference": f"Patient/{patient.id}"},
                    "effectiveDateTime": resp.timestamp.isoformat(),
                    "valueQuantity": {
                        "value": resp.rate,
                        "unit": "breaths/minute",
                        "system": "http://unitsofmeasure.org",
                        "code": "/min",
                    },
                }
            )

        for spo2 in composition.pulse_oximetry:
            observations.append(
                {
                    "resourceType": "Observation",
                    "id": f"obs-spo2-{spo2.id}",
                    "status": "final",
                    "code": {
                        "coding": [
                            {
                                "system": "http://loinc.org",
                                "code": "59408-5",
                                "display": "Oxygen saturation in Arterial blood by Pulse oximetry",
                            }
                        ],
                        "text": "Oxygen Saturation",
                    },
                    "subject": {"reference": f"Patient/{patient.id}"},
                    "effectiveDateTime": spo2.timestamp.isoformat(),
                    "valueQuantity": {
                        "value": spo2.spo2_numerator,
                        "unit": "%",
                        "system": "http://unitsofmeasure.org",
                        "code": "%",
                    },
                }
            )

    db.close()

    fhir_bundle = {
        "resourceType": "Bundle",
        "type": "collection",
        "entry": [{"resource": fhir_patient}] + [{"resource": o} for o in observations],
    }

    os.makedirs("data", exist_ok=True)
    output_path = os.path.join("data", "fhir_export.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(fhir_bundle, f, ensure_ascii=False, indent=2)

    return RedirectResponse(url="/", status_code=303)


@app.get("/")
def home(request: Request):
    db = SessionLocal()
    patient = db.query(Patient).filter_by(name="Demo Patient").first()

    measurements = []

    if patient and patient.ehr:
        for composition in patient.ehr.compositions:
            row = {
                "composition_id": composition.id,
                "patient_name": patient.name,
                "timestamp": composition.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                "heart_rate": "-",
                "blood_pressure": "-",
                "temperature": "-",
                "respiration": "-",
                "spo2": "-",
            }

            # Vezmeme první hodnotu z každého typu (pokud existuje)
            if composition.pulse:
                row["heart_rate"] = (
                    f"{composition.pulse[0].rate} {composition.pulse[0].rate_unit}"
                )
            if composition.blood_pressure:
                bp = composition.blood_pressure[0]
                row["blood_pressure"] = f"{bp.systolic}/{bp.diastolic} mmHg"
            if composition.body_temperature:
                row["temperature"] = f"{composition.body_temperature[0].temperature} °C"
            if composition.respiration:
                row["respiration"] = (
                    f"{composition.respiration[0].rate} {composition.respiration[0].rate_unit}"
                )
            if composition.pulse_oximetry:
                row["spo2"] = f"{composition.pulse_oximetry[0].spo2_numerator} %"

            measurements.append(row)

    db.close()

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "measurements": sorted(
                measurements, key=lambda x: x["timestamp"], reverse=True
            ),
        },
    )


@app.get("/composition")
def vitals_form(request: Request):
    return templates.TemplateResponse("vitals_form.html", {"request": request})


@app.get("/export/fhir/{composition_id}")
def export_fhir_composition(composition_id: int):
    db = SessionLocal()
    composition = db.query(Composition).filter_by(id=composition_id).first()

    if not composition or not composition.ehr or not composition.ehr.patient:
        db.close()
        return JSONResponse(content={"error": "Composition not found"}, status_code=404)

    patient = composition.ehr.patient
    observations = []

    fhir_patient = {
        "resourceType": "Patient",
        "id": f"{patient.id}",
        "name": [{"text": patient.name}],
        "birthDate": patient.birth_date.isoformat(),
    }

    for pulse in composition.pulse:
        observations.append(
            {
                "resourceType": "Observation",
                "id": f"obs-pulse-{pulse.id}",
                "status": "final",
                "code": {
                    "coding": [
                        {
                            "system": "http://loinc.org",
                            "code": "8867-4",
                            "display": "Heart rate",
                        }
                    ],
                    "text": "Heart Rate",
                },
                "subject": {"reference": f"Patient/{patient.id}"},
                "effectiveDateTime": pulse.timestamp.isoformat(),
                "valueQuantity": {
                    "value": pulse.rate,
                    "unit": "beats/minute",
                    "system": "http://unitsofmeasure.org",
                    "code": "/min",
                },
            }
        )

    for bp in composition.blood_pressure:
        if bp.systolic:
            observations.append(
                {
                    "resourceType": "Observation",
                    "id": f"obs-sbp-{bp.id}",
                    "status": "final",
                    "code": {
                        "coding": [
                            {
                                "system": "http://loinc.org",
                                "code": "8480-6",
                                "display": "Systolic blood pressure",
                            }
                        ],
                        "text": "Systolic BP",
                    },
                    "subject": {"reference": f"Patient/{patient.id}"},
                    "effectiveDateTime": bp.timestamp.isoformat(),
                    "valueQuantity": {
                        "value": bp.systolic,
                        "unit": "mmHg",
                        "system": "http://unitsofmeasure.org",
                        "code": "mm[Hg]",
                    },
                }
            )
        if bp.diastolic:
            observations.append(
                {
                    "resourceType": "Observation",
                    "id": f"obs-dbp-{bp.id}",
                    "status": "final",
                    "code": {
                        "coding": [
                            {
                                "system": "http://loinc.org",
                                "code": "8462-4",
                                "display": "Diastolic blood pressure",
                            }
                        ],
                        "text": "Diastolic BP",
                    },
                    "subject": {"reference": f"Patient/{patient.id}"},
                    "effectiveDateTime": bp.timestamp.isoformat(),
                    "valueQuantity": {
                        "value": bp.diastolic,
                        "unit": "mmHg",
                        "system": "http://unitsofmeasure.org",
                        "code": "mm[Hg]",
                    },
                }
            )

    for temp in composition.body_temperature:
        observations.append(
            {
                "resourceType": "Observation",
                "id": f"obs-temp-{temp.id}",
                "status": "final",
                "code": {
                    "coding": [
                        {
                            "system": "http://loinc.org",
                            "code": "8310-5",
                            "display": "Body temperature",
                        }
                    ],
                    "text": "Body Temperature",
                },
                "subject": {"reference": f"Patient/{patient.id}"},
                "effectiveDateTime": temp.timestamp.isoformat(),
                "valueQuantity": {
                    "value": temp.temperature,
                    "unit": "°C",
                    "system": "http://unitsofmeasure.org",
                    "code": "Cel",
                },
            }
        )

    for resp in composition.respiration:
        observations.append(
            {
                "resourceType": "Observation",
                "id": f"obs-resp-{resp.id}",
                "status": "final",
                "code": {
                    "coding": [
                        {
                            "system": "http://loinc.org",
                            "code": "9279-1",
                            "display": "Respiratory rate",
                        }
                    ],
                    "text": "Respiratory Rate",
                },
                "subject": {"reference": f"Patient/{patient.id}"},
                "effectiveDateTime": resp.timestamp.isoformat(),
                "valueQuantity": {
                    "value": resp.rate,
                    "unit": "breaths/minute",
                    "system": "http://unitsofmeasure.org",
                    "code": "/min",
                },
            }
        )

    for spo2 in composition.pulse_oximetry:
        observations.append(
            {
                "resourceType": "Observation",
                "id": f"obs-spo2-{spo2.id}",
                "status": "final",
                "code": {
                    "coding": [
                        {
                            "system": "http://loinc.org",
                            "code": "59408-5",
                            "display": "Oxygen saturation in Arterial blood by Pulse oximetry",
                        }
                    ],
                    "text": "Oxygen Saturation",
                },
                "subject": {"reference": f"Patient/{patient.id}"},
                "effectiveDateTime": spo2.timestamp.isoformat(),
                "valueQuantity": {
                    "value": spo2.spo2_numerator,
                    "unit": "%",
                    "system": "http://unitsofmeasure.org",
                    "code": "%",
                },
            }
        )

    db.close()

    fhir_bundle = {
        "resourceType": "Bundle",
        "type": "collection",
        "entry": [{"resource": fhir_patient}] + [{"resource": o} for o in observations],
    }

    os.makedirs("data", exist_ok=True)
    output_path = os.path.join("data", f"fhir_export_{composition_id}.json")
    print("Saving FHIR bundle to:", output_path)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(fhir_bundle, f, ensure_ascii=False, indent=2)

    return RedirectResponse(url="/", status_code=303)


@app.post("/composition")
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
    db: Session = SessionLocal()

    patient = db.query(Patient).filter_by(name="Demo Patient").first()
    if not patient:
        patient = Patient(name="Demo Patient", birth_date=date(2002, 7, 15))
        db.add(patient)
        db.commit()
        db.refresh(patient)

    ehr = db.query(EHR).filter_by(patient_id=patient.id).first()
    if not ehr:
        ehr = EHR(patient_id=patient.id)
        db.add(ehr)
        db.commit()
        db.refresh(ehr)

    context = CompositionContext()
    db.add(context)
    db.commit()
    db.refresh(context)

    composition = Composition(
        ehr_id=ehr.id,
        context_id=context.id,
        name="Vital Signs Entry",
        composer="System",
        setting="primary care",
    )
    db.add(composition)
    db.commit()
    db.refresh(composition)

    db.add(PulseOximetry(spo2_numerator=spo2_numerator, composition_id=composition.id))

    if respiration_rate is not None:
        db.add(Respiration(rate=respiration_rate, composition_id=composition.id))

    if temperature is not None:
        db.add(
            BodyTemperature(
                temperature=temperature,
                body_exposure=body_exposure,
                location=location,
                composition_id=composition.id,
            )
        )

    if pulse_rate is not None:
        db.add(
            Pulse(
                rate=pulse_rate,
                position=pulse_position,
                body_site=pulse_body_site,
                composition_id=composition.id,
            )
        )

    if systolic is not None or diastolic is not None:
        db.add(
            BloodPressure(
                systolic=systolic,
                diastolic=diastolic,
                position=bp_position,
                location=bp_location,
                composition_id=composition.id,
            )
        )

    db.commit()
    db.close()

    return RedirectResponse(url="/", status_code=303)


# .\.venv\Scripts\python.exe -m uvicorn main:app --reload
