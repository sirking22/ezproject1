#!/usr/bin/env python3
"""
Простой HTTP API сервер для работы с Notion
"""

import json
import logging
import os
from typing import Dict, Any, List
from datetime import datetime

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

from notion_client import Client

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация Notion клиента
notion = Client(auth=os.getenv("NOTION_TOKEN"))

# ID баз данных
KPI_DB = "1d6ace03d9ff80bfb809ed21dfd2150c"
RDT_DB = "195ace03d9ff80c1a1b0d236ec3564d2"

# Создаем FastAPI приложение
app = FastAPI(title="Notion API Server", version="1.0.0")

class KPIRecord(BaseModel):
    name: str
    kpi_type: str
    target_value: float
    employee_id: str
    period_start: str = "2025-07-01"
    period_end: str = "2025-07-31"
    comment: str = ""

class EmployeeSearch(BaseModel):
    employee_name: str

@app.get("/")
async def root():
    """Корневой endpoint"""
    return {"message": "Notion API Server", "version": "1.0.0"}

@app.get("/databases")
async def list_databases():
    """Список доступных баз данных"""
    return {
        "databases": {
            "kpi": {"name": "KPI и метрики", "id": KPI_DB},
            "rdt": {"name": "Сотрудники (RDT)", "id": RDT_DB}
        }
    }

@app.post("/kpi/create")
async def create_kpi_record(record: KPIRecord):
    """Создать KPI запись"""
    try:
        properties = {
            "Name": {"title": [{"text": {"content": record.name}}]},
            "Тип KPI": {"select": {"name": record.kpi_type}},
            "Целевое значение": {"number": record.target_value},
            "Сотрудники": {"relation": [{"id": record.employee_id}]},
            "Период": {"date": {"start": record.period_start, "end": record.period_end}},
            "Комментарий": {"rich_text": [{"text": {"content": record.comment}}]}
        }
        
        response = notion.pages.create(
            parent={"database_id": KPI_DB},
            properties=properties
        )
        
        return {
            "success": True,
            "message": "KPI запись создана",
            "id": response["id"],
            "url": response["url"]
        }
    except Exception as e:
        logger.error(f"Ошибка создания KPI: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/employee/search")
async def get_employee_id(search: EmployeeSearch):
    """Получить ID сотрудника по имени"""
    try:
        response = notion.databases.query(
            database_id=RDT_DB,
            page_size=100
        )
        
        employee_name = search.employee_name.lower()
        
        for page in response.get("results", []):
            props = page.get("properties", {})
            title = props.get("Сотрудник", {}).get("title", [])
            if title:
                name = title[0]["plain_text"].lower()
                if employee_name in name or name in employee_name:
                    return {
                        "success": True,
                        "employee_name": search.employee_name,
                        "employee_id": page["id"],
                        "page_url": page["url"]
                    }
        
        return {
            "success": False,
            "message": f"Сотрудник {search.employee_name} не найден"
        }
    except Exception as e:
        logger.error(f"Ошибка поиска сотрудника: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/kpi/list")
async def list_kpi_records(page_size: int = 10):
    """Получить список KPI записей"""
    try:
        response = notion.databases.query(
            database_id=KPI_DB,
            page_size=page_size
        )
        
        records = []
        for page in response.get("results", []):
            records.append({
                "id": page["id"],
                "url": page["url"],
                "created_time": page["created_time"]
            })
        
        return {
            "success": True,
            "records": records,
            "total": len(records)
        }
    except Exception as e:
        logger.error(f"Ошибка получения KPI: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/kpi/bulk_create")
async def bulk_create_kpi(records: List[KPIRecord]):
    """Массовое создание KPI записей"""
    results = []
    
    for record in records:
        try:
            properties = {
                "Name": {"title": [{"text": {"content": record.name}}]},
                "Тип KPI": {"select": {"name": record.kpi_type}},
                "Целевое значение": {"number": record.target_value},
                "Сотрудники": {"relation": [{"id": record.employee_id}]},
                "Период": {"date": {"start": record.period_start, "end": record.period_end}},
                "Комментарий": {"rich_text": [{"text": {"content": record.comment}}]}
            }
            
            response = notion.pages.create(
                parent={"database_id": KPI_DB},
                properties=properties
            )
            
            results.append({
                "success": True,
                "name": record.name,
                "id": response["id"]
            })
        except Exception as e:
            results.append({
                "success": False,
                "name": record.name,
                "error": str(e)
            })
    
    return {
        "success": True,
        "results": results,
        "total": len(records),
        "successful": len([r for r in results if r["success"]])
    }

if __name__ == "__main__":
    logger.info("🚀 Запуск Notion API Server на http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000) 