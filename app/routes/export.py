from fastapi import APIRouter, Response
from fastapi.responses import StreamingResponse
from app.models.strategy import Strategy
from app.db import get_session
from app.services.backtest_service import run_backtest_on_code
from sqlmodel import select
import io
import csv

router = APIRouter()

@router.get("/export/code/{strategy_id}")
def export_strategy_code(strategy_id: int):
    with get_session() as session:
        strategy = session.get(Strategy, strategy_id)
        if not strategy:
            return {"error": "Strategy not found"}
        
        file_content = strategy.code 
        filename = f"{strategy.name.replace(' ','_')}.py"
        return Response(content=file_content, media_type="text/x-python", headers={"Content-Disposition": f"attachment; filename={filename}"})
    

@router.get("/export/csv/{strategy_id}")
def export_strategy_csv(strategy_id: int):
    with get_session() as session:
        strategy = session.get(Strategy, strategy_id)
        if not strategy:
            return {"error": "Strategy not found"}
        
        # Run backtest to get results
    backtest_results = run_backtest_on_code(strategy.code,"RELIANCE.NS")
    if "error" in backtest_results:
        return {"error": backtest_results["error"]}
        
        # Prepare CSV data
    csv_buffer = io.StringIO()
    writer = csv.writer(csv_buffer)
    writer.writerow(["Metric", "Value"])
    for key, value in backtest_results["metrics"].items():
        writer.writerow([key, value])

    return StreamingResponse(io.StringIO(csv_buffer.getvalue()), media_type="text/csv", headers={
        "Content-Disposition": f"attachment; filename={strategy.name.replace(' ', '_')}_results.csv"
    })