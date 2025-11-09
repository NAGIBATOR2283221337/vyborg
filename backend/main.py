import os
import sys
from pathlib import Path
from io import BytesIO
import traceback

# Добавляем корневую директорию в путь для импортов
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(current_dir))

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# Импортируем процессоры
try:
    from processors import processor_rus, processor_foreign
except ImportError as e:
    print(f"Ошибка импорта процессоров: {e}")
    # Создаем заглушки для отладки
    class MockProcessor:
        @staticmethod
        def process(schedule_bytes, report_bytes, params):
            raise HTTPException(500, "Процессор не загружен")

    processor_rus = MockProcessor()
    processor_foreign = MockProcessor()

app = FastAPI(title="Обработка отчётов", description="API для обработки отчётов российских и иностранных передач")

# Добавляем CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/process/rus")
async def process_rus_report(
    schedule_file: UploadFile = File(..., description="Файл сетки"),
    report_file: UploadFile = File(..., description="Файл отчёта"),
    max_shows: int = Form(3, description="Максимальное количество показов"),
    fuzzy_cutoff: float = Form(0.05, description="Порог нечёткого поиска"),
    min_token_overlap: float = Form(0.10, description="Минимальное пересечение токенов"),
    delete_unmatched: bool = Form(False, description="Удалять несовпадающие строки")
):
    """Обработка российского отчёта"""
    try:
        # Валидация параметров
        if max_shows < 1 or max_shows > 10:
            raise HTTPException(status_code=400, detail="max_shows должен быть от 1 до 10")

        if not (0.0 <= fuzzy_cutoff <= 1.0):
            raise HTTPException(status_code=400, detail="fuzzy_cutoff должен быть от 0.0 до 1.0")

        if not (0.0 <= min_token_overlap <= 1.0):
            raise HTTPException(status_code=400, detail="min_token_overlap должен быть от 0.0 до 1.0")

        # Читаем файлы
        schedule_bytes = await schedule_file.read()
        report_bytes = await report_file.read()

        if len(schedule_bytes) == 0:
            raise HTTPException(status_code=400, detail="Файл сетки пуст")

        if len(report_bytes) == 0:
            raise HTTPException(status_code=400, detail="Файл отчёта пуст")

        # Параметры обработки
        params = {
            'max_shows': max_shows,
            'fuzzy_cutoff': fuzzy_cutoff,
            'min_token_overlap': min_token_overlap,
            'delete_unmatched': delete_unmatched
        }

        # Обрабатываем
        print(f"Начинаем обработку российского отчёта. Файлы: {schedule_file.filename}, {report_file.filename}")
        result_bytes = processor_rus.process(schedule_bytes, report_bytes, params)
        print(f"Обработка завершена успешно. Размер результата: {len(result_bytes)} байт")

        # Возвращаем файл
        return StreamingResponse(
            BytesIO(result_bytes),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=report_rus_ready.xlsx"}
        )

    except HTTPException:
        raise
    except PermissionError as e:
        print(f"Ошибка доступа к файлу: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Ошибка доступа к временным файлам. Попробуйте еще раз.")
    except Exception as e:
        print(f"Ошибка обработки российского отчёта: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Ошибка обработки: {str(e)}")


@app.post("/api/process/foreign")
async def process_foreign_report(
    schedule_file: UploadFile = File(..., description="Файл сетки"),
    report_file: UploadFile = File(..., description="Файл отчёта"),
    max_shows: int = Form(3, description="Максимальное количество показов"),
    fuzzy_cutoff: float = Form(0.05, description="Порог нечёткого поиска"),
    min_token_overlap: float = Form(0.10, description="Минимальное пересечение токенов"),
    delete_unmatched: bool = Form(False, description="Удалять несовпадающие строки")
):
    """Обработка иностранного отчёта"""
    try:
        # Валидация параметров
        if max_shows < 1 or max_shows > 10:
            raise HTTPException(status_code=400, detail="max_shows должен быть от 1 до 10")

        if not (0.0 <= fuzzy_cutoff <= 1.0):
            raise HTTPException(status_code=400, detail="fuzzy_cutoff должен быть от 0.0 до 1.0")

        if not (0.0 <= min_token_overlap <= 1.0):
            raise HTTPException(status_code=400, detail="min_token_overlap должен быть от 0.0 до 1.0")

        # Читаем файлы
        schedule_bytes = await schedule_file.read()
        report_bytes = await report_file.read()

        if len(schedule_bytes) == 0:
            raise HTTPException(status_code=400, detail="Файл сетки пуст")

        if len(report_bytes) == 0:
            raise HTTPException(status_code=400, detail="Файл отчёта пуст")

        # Параметры обработки
        params = {
            'max_shows': max_shows,
            'fuzzy_cutoff': fuzzy_cutoff,
            'min_token_overlap': min_token_overlap,
            'delete_unmatched': delete_unmatched
        }

        # Обрабатываем
        print(f"Начинаем обработку иностранного отчёта. Файлы: {schedule_file.filename}, {report_file.filename}")
        result_bytes = processor_foreign.process(schedule_bytes, report_bytes, params)
        print(f"Обработка завершена успешно. Размер результата: {len(result_bytes)} байт")

        # Возвращаем файл
        return StreamingResponse(
            BytesIO(result_bytes),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=report_foreign_ready.xlsx"}
        )

    except HTTPException:
        raise
    except PermissionError as e:
        print(f"Ошибка доступа к файлу: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Ошибка доступа к временным файлам. Попробуйте еще раз.")
    except Exception as e:
        print(f"Ошибка обработки иностранного отчёта: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Ошибка обработки: {str(e)}")


@app.get("/health")
async def health_check():
    """Проверка здоровья сервиса"""
    return {"status": "ok", "message": "Сервис работает"}


# Монтируем статические файлы в самом конце, чтобы API endpoints имели приоритет
static_path = project_root / "frontend"
if static_path.exists():
    app.mount("/", StaticFiles(directory=str(static_path), html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
