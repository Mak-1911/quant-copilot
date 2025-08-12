from app.models.strategy_blueprint import StrategyBlueprint, EntryCondition, ExitCondition, RiskManagement


def _format_condition(cond):
    details = f"{cond.indicator.upper()}"
    if cond.params.lookback:
        details += f"({cond.params.lookback})"
    if cond.operator in ["crosses_above", "crosses_below"]:
        details += f" {cond.operator.replace('_', ' ')}"
    else:
        details += f" {cond.operator} {cond.value}"
    return details


def blueprint_to_prompt(bp: StrategyBlueprint) -> str:
    entry_rules = "\n    • ".join([_format_condition(c) for c in bp.entry])
    exit_rules = "\n    • ".join([_format_condition(c) for c in bp.exit])

    risk_lines = []
    if bp.risk:
        if bp.risk.stop_loss:
            risk_lines.append(f"Stop Loss: {bp.risk.stop_loss}%")
        if bp.risk.take_profit:
            risk_lines.append(f"Take Profit: {bp.risk.take_profit}%")
        if bp.risk.trailing_stop:
            risk_lines.append(f"Trailing Stop: {bp.risk.trailing_stop}%")

    risk_block = "\n    • " + "\n    • ".join(risk_lines) if risk_lines else ""

    prompt = (
        f"Build a strategy on {bp.asset} using {bp.timeframe} candles:\n\n"
        f"- Entry Rules:\n    • {entry_rules}\n\n"
        f"- Exit Rules:\n    • {exit_rules}\n\n"
    )

    if risk_block.strip():
        prompt += f"- Risk:\n{risk_block}\n\n"

    prompt += f"- Position Sizing: {bp.position_sizing}"
    return prompt
