"""
Main CLI entry point for Cinder CLI using Click.
"""

from __future__ import annotations

import click

from cinder_cli import __version__
from cinder_cli.config import Config


@click.group()
@click.version_option(version=__version__)
@click.option(
    "--backend",
    type=click.Choice(["ollama", "claude"]),
    help="Backend to use (ollama or claude)",
)
@click.option("--model", help="Model name for Ollama backend")
@click.option("--soul", type=click.Path(exists=True), help="Path to soul.md file")
@click.option("--meta", type=click.Path(exists=True), help="Path to soul.meta.yaml file")
@click.pass_context
def cli(ctx: click.Context, backend: str, model: str, soul: str, meta: str) -> None:
    """
    Cinder CLI - A soul-guided command-line interface for personal agent interactions.
    """
    config = Config()

    if backend:
        config.set("backend", backend)
    if model:
        config.set("model", model)
    if soul:
        config.set("soul_path", soul)
    if meta:
        config.set("meta_path", meta)

    ctx.ensure_object(dict)
    ctx.obj["config"] = config


@cli.command()
@click.option("--output", default="soul.md", help="Output path for soul.md")
@click.option("--name", default="", help="Name of the person being analyzed")
@click.option("--quick", is_flag=True, help="Quick mode with default values")
@click.option("--resume", is_flag=True, help="Resume incomplete session")
@click.option("--skip-confirmation", is_flag=True, help="Skip soul confirmation")
@click.pass_context
def init(
    ctx: click.Context,
    output: str,
    name: str,
    quick: bool,
    resume: bool,
    skip_confirmation: bool,
) -> None:
    """
    Initialize soul profile through interactive question guidance.
    """
    from cinder_cli.question_guide import QuestionGuide

    guide = QuestionGuide(output_path=output, name=name, quick_mode=quick)
    
    if resume:
        guide.resume_session()
    else:
        guide.run()
    
    if not skip_confirmation:
        from cinder_cli.soul_presenter import SoulPresenter
        
        presenter = SoulPresenter(output)
        presenter.present_and_confirm()


@cli.command()
@click.option("--skip-confirmation", is_flag=True, help="Skip confirmation prompts")
@click.pass_context
def confirm(ctx: click.Context, skip_confirmation: bool) -> None:
    """
    Confirm and adjust existing soul profile.
    """
    from cinder_cli.soul_presenter import SoulPresenter

    config: Config = ctx.obj["config"]
    soul_path = config.get("soul_path", "soul.md")
    
    presenter = SoulPresenter(soul_path)
    presenter.present_and_confirm(skip_confirmation)


@cli.command()
@click.option("--message", help="Single message to send (non-interactive mode)")
@click.option("--temperature", type=float, help="Model temperature")
@click.option("--reflection-loop", is_flag=True, help="Enable reflection loop (Claude only)")
@click.option("--proxy", is_flag=True, help="Enable proxy decision mode")
@click.option("--no-logging", is_flag=True, help="Disable decision logging")
@click.pass_context
def chat(
    ctx: click.Context,
    message: str,
    temperature: float,
    reflection_loop: bool,
    proxy: bool,
    no_logging: bool,
) -> None:
    """
    Start chat session with soul-guided agent.
    """
    from cinder_cli.chat_handler import ChatHandler

    config: Config = ctx.obj["config"]
    
    if temperature:
        config.set("temperature", temperature)
    if reflection_loop:
        config.set("reflection_loop", reflection_loop)
    if proxy:
        config.set("proxy_mode", proxy)
    if no_logging:
        config.set("decision_logging", False)

    handler = ChatHandler(config)
    
    if message:
        handler.run_single(message)
    else:
        handler.run_interactive()


@cli.group()
@click.pass_context
def decisions(ctx: click.Context) -> None:
    """
    Manage decision logs and statistics.
    """
    pass


@decisions.command("list")
@click.option("--limit", default=10, help="Number of decisions to show")
@click.option("--from", "from_date", help="Start date (ISO format)")
@click.option("--to", "to_date", help="End date (ISO format)")
@click.option("--min-confidence", type=float, help="Minimum confidence score")
@click.option("--search", help="Search in decision context")
@click.pass_context
def list_decisions(
    ctx: click.Context,
    limit: int,
    from_date: str,
    to_date: str,
    min_confidence: float,
    search: str,
) -> None:
    """
    List decision history with optional filters.
    """
    from cinder_cli.decision_logger import DecisionLogger

    config: Config = ctx.obj["config"]
    logger = DecisionLogger(config.database_path)
    
    decisions_list = logger.list_decisions(
        limit=limit,
        min_confidence=min_confidence,
        from_date=from_date,
        to_date=to_date,
        search=search,
    )
    
    if not decisions_list:
        click.echo("No decisions found.")
        return
    
    for decision in decisions_list:
        click.echo(f"\n[{decision['id']}] {decision['timestamp']}")
        click.echo(f"  Confidence: {decision['confidence']:.2f}")
        click.echo(f"  Requires Human: {decision['requires_human']}")
        click.echo(f"  Context: {str(decision['context'])[:100]}...")


@decisions.command("show")
@click.argument("decision_id", type=int)
@click.option("--reasoning", is_flag=True, help="Show reasoning chain")
@click.option("--format", type=click.Choice(["text", "json"]), default="text")
@click.pass_context
def show_decision(
    ctx: click.Context, decision_id: int, reasoning: bool, format: str
) -> None:
    """
    Show detailed information about a specific decision.
    """
    from cinder_cli.decision_logger import DecisionLogger

    config: Config = ctx.obj["config"]
    logger = DecisionLogger(config.database_path)
    
    decision = logger.get_decision(decision_id)
    if not decision:
        click.echo(f"Decision {decision_id} not found.", err=True)
        return
    
    if format == "json":
        import json
        click.echo(json.dumps(decision, indent=2, ensure_ascii=False))
    else:
        click.echo(f"\nDecision ID: {decision['id']}")
        click.echo(f"Timestamp: {decision['timestamp']}")
        click.echo(f"Confidence: {decision['confidence']:.2f}")
        click.echo(f"Requires Human: {decision['requires_human']}")
        click.echo(f"\nContext:")
        click.echo(str(decision['context']))
        click.echo(f"\nSoul Rules Applied:")
        click.echo(str(decision['soul_rules']))
        click.echo(f"\nDecision:")
        click.echo(str(decision['decision']))
        
        if reasoning:
            click.echo(f"\nReasoning Chain:")
            if 'reasoning' in decision['decision']:
                click.echo(decision['decision']['reasoning'])


@decisions.command("stats")
@click.option("--confidence-distribution", is_flag=True, help="Show confidence distribution")
@click.option("--top-rules", is_flag=True, help="Show frequently applied rules")
@click.pass_context
def stats(ctx: click.Context, confidence_distribution: bool, top_rules: bool) -> None:
    """
    Show decision statistics and insights.
    """
    from cinder_cli.decision_logger import DecisionLogger

    config: Config = ctx.obj["config"]
    logger = DecisionLogger(config.database_path)
    
    statistics = logger.get_statistics()
    
    click.echo("\nDecision Statistics:")
    click.echo(f"  Total Decisions: {statistics['total']}")
    click.echo(f"  Average Confidence: {statistics['avg_confidence']:.2f}")
    click.echo(f"  Requires Human: {statistics['requires_human_count']}")
    click.echo(f"  Reviewed: {statistics['reviewed_count']}")


@decisions.command("export")
@click.option("--format", type=click.Choice(["csv", "json"]), default="json")
@click.option("--output", type=click.Path(), help="Output file path")
@click.option("--from", "from_date", help="Start date (ISO format)")
@click.option("--to", "to_date", help="End date (ISO format)")
@click.pass_context
def export_decisions(
    ctx: click.Context,
    format: str,
    output: str,
    from_date: str,
    to_date: str,
) -> None:
    """
    Export decision logs to CSV or JSON.
    """
    from cinder_cli.decision_logger import DecisionLogger

    config: Config = ctx.obj["config"]
    logger = DecisionLogger(config.database_path)
    
    decisions_list = logger.list_decisions(
        limit=10000,
        from_date=from_date,
        to_date=to_date,
    )
    
    if format == "json":
        import json
        output_content = json.dumps(decisions_list, indent=2, ensure_ascii=False)
    else:
        import csv
        import io
        output_buffer = io.StringIO()
        if decisions_list:
            writer = csv.DictWriter(output_buffer, fieldnames=decisions_list[0].keys())
            writer.writeheader()
            writer.writerows(decisions_list)
        output_content = output_buffer.getvalue()
    
    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(output_content)
        click.echo(f"Exported {len(decisions_list)} decisions to {output}")
    else:
        click.echo(output_content)


@decisions.command("clean")
@click.option("--older-than", type=int, help="Delete decisions older than N days")
@click.option("--archive", is_flag=True, help="Archive before deletion")
@click.pass_context
def clean_decisions(ctx: click.Context, older_than: int, archive: bool) -> None:
    """
    Clean up old decision logs.
    """
    from cinder_cli.decision_logger import DecisionLogger

    config: Config = ctx.obj["config"]
    logger = DecisionLogger(config.database_path)
    
    if older_than:
        count = logger.delete_old_decisions(older_than, archive)
        click.echo(f"Deleted {count} decisions older than {older_than} days")
    else:
        click.echo("Please specify --older-than option")


@decisions.command("review")
@click.argument("decision_id", type=int, required=False)
@click.option("--correct", is_flag=True, help="Mark decision as correct")
@click.option("--incorrect", is_flag=True, help="Mark decision as incorrect")
@click.option("--reason", help="Reason for the review")
@click.option("--pending", is_flag=True, help="Show decisions pending review")
@click.pass_context
def review_decision(
    ctx: click.Context,
    decision_id: int,
    correct: bool,
    incorrect: bool,
    reason: str,
    pending: bool,
) -> None:
    """
    Review and provide feedback on proxy decisions.
    """
    from cinder_cli.decision_logger import DecisionLogger

    config: Config = ctx.obj["config"]
    logger = DecisionLogger(config.database_path)
    
    if pending:
        decisions_list = logger.list_decisions(limit=20)
        unreviewed = [d for d in decisions_list if not d['reviewed']]
        if not unreviewed:
            click.echo("No decisions pending review.")
            return
        for decision in unreviewed:
            click.echo(f"\n[{decision['id']}] {decision['timestamp']}")
            click.echo(f"  Confidence: {decision['confidence']:.2f}")
        return
    
    if not decision_id:
        click.echo("Please provide a decision ID or use --pending flag", err=True)
        return
    
    if correct:
        logger.update_review(decision_id, True, "correct", reason)
        click.echo(f"Decision {decision_id} marked as correct")
    elif incorrect:
        logger.update_review(decision_id, True, "incorrect", reason)
        click.echo(f"Decision {decision_id} marked as incorrect")
    else:
        click.echo("Please specify --correct or --incorrect", err=True)


@cli.command()
@click.argument("key", required=False)
@click.argument("value", required=False)
@click.option("--list", "list_all", is_flag=True, help="List all configuration")
@click.option("--reset", is_flag=True, help="Reset to default configuration")
@click.pass_context
def config_cmd(
    ctx: click.Context, key: str, value: str, list_all: bool, reset: bool
) -> None:
    """
    Manage configuration settings.
    """
    config: Config = ctx.obj["config"]
    
    if reset:
        config.reset()
        click.echo("Configuration reset to defaults.")
        return
    
    if list_all:
        click.echo("Current configuration:")
        for k, v in config.all.items():
            click.echo(f"  {k}: {v}")
        return
    
    if key and value:
        config.set(key, value)
        click.echo(f"Set {key} = {value}")
    elif key:
        click.echo(f"{key}: {config.get(key)}")
    else:
        click.echo("Please specify a key or use --list to show all configuration")


cli.add_command(config_cmd, name="config")


def main() -> None:
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()
