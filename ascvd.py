from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import math

# Initialize FastAPI app
app = FastAPI()

# Define input schema
class ASCVDInput(BaseModel):
    is_male: bool
    is_black: bool
    smoker: bool
    hypertensive: bool
    diabetic: bool
    age: int
    systolic_bp: int
    diastolic_bp: int
    total_cholesterol: int
    hdl: int
    ldl: int

# ASCVD calculator function
def calculate_ascvd_risk(
    is_male: bool,
    is_black: bool,
    smoker: bool,
    hypertensive: bool,
    diabetic: bool,
    age: int,
    systolic_bp: int,
    diastolic_bp: int,
    total_cholesterol: int,
    hdl: int,
    ldl: int,
):
    # Validate input ranges
    if not (40 <= age <= 79):
        raise HTTPException(status_code=400, detail="Age must be between 40 and 79.")
    if not (90 <= systolic_bp <= 200):
        raise HTTPException(status_code=400, detail="Systolic BP must be between 90 and 200 mmHg.")
    if not (60 <= diastolic_bp <= 130):
        raise HTTPException(status_code=400, detail="Diastolic BP must be between 60 and 130 mmHg.")
    if not (130 <= total_cholesterol <= 320):
        raise HTTPException(status_code=400, detail="Total cholesterol must be between 130 and 320 mg/dL.")
    if not (20 <= hdl <= 100):
        raise HTTPException(status_code=400, detail="HDL cholesterol must be between 20 and 100 mg/dL.")
    if not (30 <= ldl <= 300):
        raise HTTPException(status_code=400, detail="LDL cholesterol must be between 30 and 300 mg/dL.")

    # Logarithmic calculations
    ln_age = math.log(age)
    ln_total_chol = math.log(total_cholesterol)
    ln_hdl = math.log(hdl)
    tr_ln_sbp = math.log(systolic_bp) if hypertensive else 0
    nt_ln_sbp = 0 if hypertensive else math.log(systolic_bp)
    age_total_chol = ln_age * ln_total_chol
    age_hdl = ln_age * ln_hdl
    age_tr_sbp = ln_age * tr_ln_sbp
    age_nt_sbp = ln_age * nt_ln_sbp
    age_smoke = ln_age if smoker else 0

    # Race and gender-based calculation
    if is_black and not is_male:
        s010 = 0.95334
        mnxb = 86.6081
        predict = (
            17.1141 * ln_age
            + 0.9396 * ln_total_chol
            - 18.9196 * ln_hdl
            + 4.4748 * age_hdl
            + 29.2907 * tr_ln_sbp
            - 6.4321 * age_tr_sbp
            + 27.8197 * nt_ln_sbp
            - 6.0873 * age_nt_sbp
            + (0.6908 if smoker else 0)
            + (0.8738 if diabetic else 0)
        )
    elif not is_black and not is_male:
        s010 = 0.96652
        mnxb = -29.1817
        predict = (
            -29.799 * ln_age
            + 4.884 * ln_age**2
            + 13.54 * ln_total_chol
            - 3.114 * age_total_chol
            - 13.578 * ln_hdl
            + 3.149 * age_hdl
            + 2.019 * tr_ln_sbp
            + 1.957 * nt_ln_sbp
            + (7.574 if smoker else 0)
            - 1.665 * age_smoke
            + (0.661 if diabetic else 0)
        )
    elif is_black and is_male:
        s010 = 0.89536
        mnxb = 19.5425
        predict = (
            2.469 * ln_age
            + 0.302 * ln_total_chol
            - 0.307 * ln_hdl
            + 1.916 * tr_ln_sbp
            + 1.809 * nt_ln_sbp
            + (0.549 if smoker else 0)
            + (0.645 if diabetic else 0)
        )
    else:
        s010 = 0.91436
        mnxb = 61.1816
        predict = (
            12.344 * ln_age
            + 11.853 * ln_total_chol
            - 2.664 * age_total_chol
            - 7.99 * ln_hdl
            + 1.769 * age_hdl
            + 1.797 * tr_ln_sbp
            + 1.764 * nt_ln_sbp
            + (7.837 if smoker else 0)
            - 1.795 * age_smoke
            + (0.658 if diabetic else 0)
        )

    # Calculate risk percentage
    risk = 1 - s010**math.exp(predict - mnxb)
    return round(risk * 1000) / 10  # Risk in percentage rounded to one decimal place


# FastAPI route
@app.post("/calculate-ascvd-risk")
def calculate_risk(input_data: ASCVDInput):
    result = calculate_ascvd_risk(
        is_male=input_data.is_male,
        is_black=input_data.is_black,
        smoker=input_data.smoker,
        hypertensive=input_data.hypertensive,
        diabetic=input_data.diabetic,
        age=input_data.age,
        systolic_bp=input_data.systolic_bp,
        diastolic_bp=input_data.diastolic_bp,
        total_cholesterol=input_data.total_cholesterol,
        hdl=input_data.hdl,
        ldl=input_data.ldl,
    )
    return {"ascvd_risk": result}
