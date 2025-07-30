from app.models.strategy_blueprint import StrategyBlueprint

def from_blueprint_to_prompt(bp: StrategyBlueprint) -> str:
    entry = bp.entry
    exit = bp.exit
    entry_line = f"{entry.indicator.upper()} entry"
    if entry.params.lookback:
        entry_line += f" with {entry.params.lookback}-day lookback"
    if entry.params.threshold is not None:
        entry_line += f" when value crosses {entry.params.threshold}"

    exit_line = f"{exit.indicator.upper()} exit"
    if exit.params.multiplier:
        exit_line += f" using {exit.params.multiplier}x multiplier"

    prompt = (
        f"Create a trading strategy for {bp.asset}. "
        f"Enter based on {entry_line}. "
        f"Exit based on {exit_line}."
    )

    return prompt