import uvicorn
import io
import base64
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import Response, HTMLResponse
from fastapi.templating import Jinja2Templates
from src.haw import weight_score, height_score, haw_score
from src.haw import get_height_and_weight_plot, get_haw_plot, get_plots
from src.haw import bmd_score


app = FastAPI()
app.mount('/static', StaticFiles(directory='static', html=True), name='static')
templates = Jinja2Templates(directory='static')


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(
        'index.html', context={'request': request}
        )


@app.get("/submit", response_class=HTMLResponse)
async def submit(
    request: Request, sex: str, age: int, height: int, weight: float
):
    my_stringIObytes = io.BytesIO()
    get_height_and_weight_plot(
        sex, age, height, weight
        ).savefig(my_stringIObytes, format='jpg')
    my_stringIObytes.seek(0)
    encoded_score = base64.b64encode(my_stringIObytes.read()).decode()
    my_stringIObytes = io.BytesIO()
    encoded_haw = get_haw_plot(
        sex, age, height, weight
        ).savefig(my_stringIObytes, format='jpg')
    my_stringIObytes.seek(0)
    encoded_haw = base64.b64encode(my_stringIObytes.read()).decode()
    return templates.TemplateResponse(
        'index.html', context={
            'request': request,
            'sex': sex,
            'age': age,
            'height': height,
            'weight': weight,
            'height_score': f'{height_score(sex, age, height):.1f}',
            'weight_score': f'{weight_score(sex, age, weight):.1f}',
            'haw_score': f'{haw_score(sex, age, height, weight):.1f}',
            "img": encoded_score,
            "img2": encoded_haw
        })


@app.get("/get_score", response_class=HTMLResponse)
async def get_score(
    request: Request,
    secondary_amenorrhea: bool,
    bmi: float,
    fracture_history: bool,
    high_exercise_load: bool,
    age_at_menarche: int = -1,
    current_amenorrhea_duration: int = 0
):
    score = bmd_score(
        age_at_menarche,
        secondary_amenorrhea,
        current_amenorrhea_duration,
        bmi,
        fracture_history,
        high_exercise_load
    )
    return templates.TemplateResponse(
        'bone_mineral_density.html', context={
          'request': request,
          'score': score,
          'age_at_menarche': age_at_menarche if age_at_menarche != -1 else "",
          'secondary_amenorrhea': secondary_amenorrhea,
          'current_amenorrhea_duration': current_amenorrhea_duration,
          'bmi': bmi,
          'fracture_history': fracture_history,
          'high_exercise_load': high_exercise_load
        })


@app.get("/low_bmd", response_class=HTMLResponse)
async def low_bmd(request: Request):
    return templates.TemplateResponse(
        'bone_mineral_density.html',
        context={'request': request}
    )


@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    return templates.TemplateResponse(
        'about.html',
        context={'request': request}
    )


@app.get("/create_pdf")
async def create_pdf(sex: str, age: int, height: int, weight: float):
    buffer = io.BytesIO()
    get_plots(
        sex, age, height, weight, figsize=(8.27, 11.69)
        ).savefig(buffer, format='pdf')
    buffer.seek(0)

    headers = {'Content-Disposition': 'attachment; filename="results.pdf"'}
    return Response(
        buffer.getvalue(),
        headers=headers,
        media_type='application/pdf'
        )

if (__name__ == "__main__"):
    uvicorn.run(
        "main:app",
        host='127.0.0.1',
        port=8000,
        reload=True
        )
