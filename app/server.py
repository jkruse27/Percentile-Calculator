import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from haw import weight_score, height_score, haw_score
from haw import get_height_and_weight_plot, get_haw_plot, get_plots


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/submit")
async def submit(sex: str, age: int, height: int, weight: float):
    get_height_and_weight_plot(
        sex, age, height, weight
        ).savefig('static/height_weight_plot.png', format='png')
    get_haw_plot(
        sex, age, height, weight
        ).savefig('static/haw_plot.png', format='png')
    return {
        'sex': sex,
        'age': age,
        'height': height,
        'weight': weight,
        'height_score': height_score(sex, age, height),
        'weight_score': weight_score(sex, age, weight),
        'haw_score': haw_score(sex, age, height, weight)
    }


@app.get("/create_pdf")
async def create_pdf(sex: str, age: int, height: int, weight: float):
    get_plots(
        sex, age, height, weight, figsize=(8.27, 11.69)
        ).savefig('static/results.pdf', format='pdf')

    return FileResponse(path='static/results.pdf')

if (__name__ == "__main__"):
    uvicorn.run(
        "server:app",
        host='127.0.0.1',
        port=8000,
        reload=True
        )
