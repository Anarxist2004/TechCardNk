import cv2
import numpy as np
import task
import protocol


# SERVER IMPORTS
from fastapi import FastAPI, UploadFile, File, Request, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uuid
from datetime import datetime
from pathlib import Path
import json
import shutil
# /SERVER IMPORTS


def get_pic2(path_img, accuracy):
    """
    Обработка снимка с целью обнаружения границ шва
    """
    with open(path_img, 'rb') as f:
        img_bytes = f.read()

    if len(img_bytes) == 0:
        return "Файл пустой"

    # Декодирование из байтов
    img_array = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    base_img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    height, width, _ = img.shape
 
    # Самое главное - brightness_matrix, с ней мы дальше работаем
    brightness_matrix = task.get_brightness_matrix(img)

    # Подсчет среднего значения фона
    sum_bright = 0
    for i in range(height):
        for j in brightness_matrix[i]:
            sum_bright += float(j)
    # Среднее значение
    middle = sum_bright / (width * height)

    # Увеличение яркости и контрастности в зависимости от того насколько яркая картинка сейчас
    print(middle)
    if middle > 0.25: 
        # снимок светлый
        img = cv2.add(img, -100)  
        img = cv2.convertScaleAbs(img, alpha=9, beta=0)  
    else:
        # снимок тёмный
        img = cv2.convertScaleAbs(img, alpha=4, beta=0)  

    # ============ переделываем занво матрицу освещенности после обработки
    # Матрица освещённости
    brightness_matrix = task.get_brightness_matrix(img)

    # Подсчет среднего значения освещённости фона
    sum_bright = 0
    for i in range(height):
        for j in brightness_matrix[i]:
            sum_bright += float(j)
    # Среднее значение
    middle = sum_bright / (width * height)
    # ============ ///// переделываем занво матрицу освещенности после обработки

    # Транспонирование матрицы снимка
    trans_brightness_matrix = [[0 for _ in range(height)] for _ in range(width)]
    for i in range(height):
        for j in range(width):
            trans_brightness_matrix[j][i] = brightness_matrix[i][j]

    trans_width = height
    trans_height = width

    # Поиск максимального дельта-освещения в каждом ряду
    dt_id_array_top = []
    for i in trans_brightness_matrix:
        max_delta_id, max_delta = 0, 0
        for j in range(trans_width):
            delta_value = abs(middle-float(i[j])) 
            if delta_value > max_delta:
                max_delta = delta_value
                max_delta_id = j
        dt_id_array_top.append(max_delta_id)

    # Исключение выбросов
    dt_id_array_top = task.simple_clean_outliers(dt_id_array_top, accuracy)

    # Поиск максимального дельта-освещения снизу-вверх
    dt_id_array_bottom = []
    for i in trans_brightness_matrix:
        max_delta_id, max_delta = 0, 0
        for j in range(trans_width, 0, -1):
            delta_value = abs(middle-float(i[j-1]))
            if delta_value > max_delta:
                max_delta = delta_value
                max_delta_id = j
        dt_id_array_bottom.append(max_delta_id)

    # Исключение выбросов
    dt_id_array_bottom = task.simple_clean_outliers(dt_id_array_bottom, accuracy)

    # Расчет точек для центра
    middle_line_array = []
    sum_bort = 0 # bort - ширина шва / 2
    for i in range(width):
        bort = (dt_id_array_bottom[i] - dt_id_array_top[i]) / 2
        coord = int(dt_id_array_top[i] + bort)
        sum_bort += bort
        middle_line_array.append(coord)

    # Среднее расстояние от середины до края шва
    bort = sum_bort / width

    # Исключение выбросов
    middle_line_array = task.simple_clean_outliers(middle_line_array, accuracy * 2)

    # Расчет k и b
    arr_x = [0] * width
    counter = 0
    for i in range(width):
        arr_x[i] += counter
        counter+= 1
    x = np.array(arr_x)
    y = np.array([p for p in middle_line_array])
    k, b = np.polyfit(x, y, 1)

    # Отрисовка центра
    y1_middle = int(k + b)
    y2_middle = int(k*width + b)
    cv2.line(base_img, (0, y1_middle), (width, y2_middle), (120, 0, 0), 2)

    # Отрисовка верхней границы
    y1_top = int(y1_middle - bort)
    y2_top = int(y2_middle - bort)
    cv2.line(base_img, (0, y1_top), (width, y2_top), (0, 0, 120), 2)

    # Отрисовка нижней границы
    y1_bottom = int(y1_middle + bort)
    y2_bottom = int(y2_middle + bort)
    cv2.line(base_img, (0, y1_bottom), (width, y2_bottom), (0, 0, 120), 2)

    return [y1_middle, y2_middle, y1_top, y2_top, y1_bottom, y2_bottom, width, height]

MAX_SHOV_PROCESS_SIDE = 1800
MAX_SHOV_PROCESS_PIXELS = 2_500_000


def get_pic2_optimized(path_img, accuracy):
    with open(path_img, "rb") as f:
        img_bytes = f.read()

    if not img_bytes:
        raise ValueError("Файл изображения пустой")

    img_array = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Не удалось прочитать изображение")

    original_height, original_width, _ = img.shape
    if original_width < 2 or original_height < 2:
        raise ValueError("Изображение слишком маленькое для построения шва")

    max_side_scale = MAX_SHOV_PROCESS_SIDE / max(original_width, original_height)
    pixel_scale = (MAX_SHOV_PROCESS_PIXELS / (original_width * original_height)) ** 0.5
    scale = min(1.0, max_side_scale, pixel_scale)

    if scale < 1.0:
        process_width = max(2, int(original_width * scale))
        process_height = max(2, int(original_height * scale))
        img = cv2.resize(img, (process_width, process_height), interpolation=cv2.INTER_AREA)
    else:
        process_height, process_width = original_height, original_width

    brightness_matrix = task.get_brightness_matrix(img)
    middle = float(np.mean(brightness_matrix))

    if middle > 0.25:
        img = cv2.add(img, -100)
        img = cv2.convertScaleAbs(img, alpha=9, beta=0)
    else:
        img = cv2.convertScaleAbs(img, alpha=4, beta=0)

    brightness_matrix = task.get_brightness_matrix(img)
    middle = float(np.mean(brightness_matrix))
    delta = np.abs(brightness_matrix - middle)

    top = np.argmax(delta, axis=0).astype(np.float32)
    top = task.simple_clean_outliers(top, accuracy)

    bottom = (process_height - np.argmax(delta[::-1, :], axis=0)).astype(np.float32)
    bottom = task.simple_clean_outliers(bottom, accuracy)

    half_width_by_column = (bottom - top) / 2
    half_width = float(np.mean(half_width_by_column))
    center_line = task.simple_clean_outliers(top + half_width_by_column, accuracy * 2)

    x = np.arange(process_width, dtype=np.float32)
    y = np.asarray(center_line, dtype=np.float32)
    k, b = np.polyfit(x, y, 1)

    y_scale = original_height / process_height

    def to_original_y(value):
        return int(np.clip(round(value * y_scale), 0, original_height))

    y1_middle = float(b)
    y2_middle = float(k * process_width + b)

    return [
        to_original_y(y1_middle),
        to_original_y(y2_middle),
        to_original_y(y1_middle - half_width),
        to_original_y(y2_middle - half_width),
        to_original_y(y1_middle + half_width),
        to_original_y(y2_middle + half_width),
        original_width,
        original_height,
    ]


get_pic2 = get_pic2_optimized


#  SERVER
app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PY_DIR = Path(__file__).resolve().parent
BASE_DIR = PY_DIR.parent


# GET /
@app.get("/", response_class=HTMLResponse)
def root():
    filepath = BASE_DIR / "index.html"
    if not filepath.exists():
        raise HTTPException(404)    
    return filepath.read_text(encoding="utf-8")

# GET /download_annotation
@app.get("/download_annotation")
def download_annotation():
    annotations_dir = BASE_DIR / "annotations"
    annotations_dir.mkdir(parents=True, exist_ok=True)
    filepath = annotations_dir / "annotation.json"
    if not filepath.exists():
        raise HTTPException(404, "File not found")

    return FileResponse(
        path=filepath,
        filename="annotation.json",
        media_type="application/json"
    )

# POST /find_shov
@app.post("/find_shov")
async def find_shov(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(400, "No file uploaded")

    # Генерация имени
    filename = f"shov_image_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.png"
    filepath = Path(__file__).parent / filename

    # Сохранение файла
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Вызов функции работы с изображением
    coords = get_pic2(str(filepath), 2)

    return {
        "status": "success",
        "filename": filename,
        "path": str(filepath),
        "coordinates": coords,
    }

# POST /save_annotation
@app.post("/save_annotation")
async def save_annotation(request: Request):
    data = await request.json()

    filepath = BASE_DIR / "annotations" / "annotation.json"

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return {"status": "ok"}

# POST /save_protocol_docx
@app.post("/save_protocol_docx")
async def save_protocol_docx(request: Request):
    data = await request.json()

    template_path = PY_DIR / "protocol_docx.docx"
    output = protocol.build_protocol_doc(data, template_path)

    filepath = PY_DIR / "protocol_generated.docx"

    with open(filepath, "wb") as f:
        f.write(output.getvalue())

    if not filepath.exists():
        raise HTTPException(404, "DOCX not found")

    return FileResponse(
        path=filepath,
        filename="protocol.docx",
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

# Статические файлы
from fastapi.staticfiles import StaticFiles
app.mount("/static", StaticFiles(directory=BASE_DIR, html=True), name="static")

# Страница 404
@app.get("/{full_path:path}")
async def spa_fallback(full_path: str):
    print("404 Ресурс не найден")
    return FileResponse(BASE_DIR / "error.html")
