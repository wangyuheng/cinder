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
@click.argument("goal")
@click.option("--mode", type=click.Choice(["auto", "interactive", "dry-run"]), default="auto", help="Execution mode")
@click.option("--constraint", multiple=True, help="Constraints (key=value format)")
@click.option("--language", default="python", help="Programming language for code generation")
@click.option("--framework", help="Framework to use (e.g., fastapi, flask)")
@click.pass_context
def execute(
    ctx: click.Context,
    goal: str,
    mode: str,
    constraint: tuple[str, ...],
    language: str,
    framework: str | None,
) -> None:
    """
    Execute a goal autonomously using AI.
    
    Example:
        cinder execute "创建一个Python Hello World程序"
        cinder execute "做个记账web应用" --mode interactive
        cinder execute "创建API" --framework fastapi --language python
    """
    from cinder_cli.executor import AutonomousExecutor

    config: Config = ctx.obj["config"]
    
    # Parse constraints
    constraints = {}
    for c in constraint:
        if "=" in c:
            key, value = c.split("=", 1)
            constraints[key.strip()] = value.strip()
    
    if framework:
        constraints["framework"] = framework
    if language:
        constraints["language"] = language
    
    # Create executor and run
    executor = AutonomousExecutor(config)
    
    try:
        result = executor.execute(goal, mode=mode, constraints=constraints)
        
        if result["status"] == "success":
            click.echo(f"\n✓ 执行成功！")
            click.echo(f"创建了 {len(result.get('results', []))} 个文件")
        elif result["status"] == "dry-run":
            click.echo("\n预览完成，未创建实际文件")
    except Exception as e:
        click.echo(f"\n✗ 执行失败: {e}", err=True)


@cli.group()
@click.pass_context
def execution(ctx: click.Context) -> None:
    """
    Manage execution history and logs.
    """
    pass


@execution.command("list")
@click.option("--limit", default=10, help="Number of executions to show")
@click.option("--status", type=click.Choice(["success", "failed", "all"]), default="all", help="Filter by status")
@click.pass_context
def list_executions(
    ctx: click.Context,
    limit: int,
    status: str,
) -> None:
    """
    List execution history.
    """
    from cinder_cli.executor import ExecutionLogger

    config: Config = ctx.obj["config"]
    logger = ExecutionLogger(config)
    
    status_filter = None if status == "all" else status
    executions = logger.list_executions(limit=limit, status=status_filter)
    
    if not executions:
        click.echo("No executions found.")
        return
    
    for execution in executions:
        click.echo(f"\n[{execution['id']}] {execution['timestamp']}")
        click.echo(f"  Goal: {execution['goal'][:100]}...")
        click.echo(f"  Status: {execution['status']}")
        click.echo(f"  Files: {len(execution.get('created_files', []))}")


@execution.command("show")
@click.argument("execution_id", type=int)
@click.option("--format", type=click.Choice(["text", "json"]), default="text")
@click.pass_context
def show_execution(
    ctx: click.Context,
    execution_id: int,
    format: str,
) -> None:
    """
    Show detailed information about a specific execution.
    """
    from cinder_cli.executor import ExecutionLogger

    config: Config = ctx.obj["config"]
    logger = ExecutionLogger(config)
    
    execution = logger.get_execution(execution_id)
    if not execution:
        click.echo(f"Execution {execution_id} not found.", err=True)
        return
    
    if format == "json":
        import json
        click.echo(json.dumps(execution, indent=2, ensure_ascii=False))
    else:
        click.echo(f"\nExecution ID: {execution['id']}")
        click.echo(f"Timestamp: {execution['timestamp']}")
        click.echo(f"Goal: {execution['goal']}")
        click.echo(f"Status: {execution['status']}")
        click.echo(f"\nCreated Files:")
        for file_path in execution.get('created_files', []):
            click.echo(f"  - {file_path}")


@execution.command("rollback")
@click.argument("execution_id", type=int)
@click.pass_context
def rollback_execution(ctx: click.Context, execution_id: int) -> None:
    """
    Rollback files created by an execution.
    """
    from cinder_cli.executor import ExecutionLogger, FileOperations

    config: Config = ctx.obj["config"]
    logger = ExecutionLogger(config)
    
    execution = logger.get_execution(execution_id)
    if not execution:
        click.echo(f"Execution {execution_id} not found.", err=True)
        return
    
    created_files = execution.get('created_files', [])
    if not created_files:
        click.echo("No files to rollback.")
        return
    
    click.echo(f"Will delete {len(created_files)} files:")
    for file_path in created_files:
        click.echo(f"  - {file_path}")
    
    if click.confirm("Proceed with rollback?"):
        file_ops = FileOperations(config)
        for file_path in created_files:
            try:
                file_ops.delete_file(file_path, backup=True)
            except Exception as e:
                click.echo(f"  Failed to delete {file_path}: {e}")
        
        click.echo("\n✓ Rollback complete")


@execution.command()
@click.pass_context
def stats(ctx: click.Context) -> None:
    """Show execution statistics and analysis."""
    from rich.console import Console
    from rich.table import Table
    
    config: Config = ctx.obj["config"]
    logger = ExecutionLogger(config)
    console = Console()
    
    executions = logger.list_executions(limit=100)
    
    if not executions:
        console.print("[yellow]No executions found.[/yellow]")
        return
    
    total = len(executions)
    success_count = sum(1 for e in executions if e.get("status") == "success")
    total_files = sum(len(e.get("created_files", [])) for e in executions)
    
    console.print("\n[bold cyan]执行统计[/bold cyan]\n")
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("指标", style="cyan")
    table.add_column("值", justify="right")
    
    table.add_row("总执行次数", str(total))
    table.add_row("成功次数", str(success_count))
    table.add_row("成功率", f"{success_count/total*100:.1f}%")
    table.add_row("创建文件总数", str(total_files))
    table.add_row("平均文件数/执行", f"{total_files/total:.1f}")
    
    console.print(table)
    
    patterns = logger.analyze_patterns()
    if patterns.get("insights"):
        console.print("\n[bold cyan]模式分析[/bold cyan]")
        for insight in patterns["insights"]:
            console.print(f"  • {insight}")


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


@cli.command()
@click.option("--host", default="localhost", help="Host to bind server")
@click.option("--port", default=8000, help="Port for API server")
@click.option("--frontend-port", default=3000, help="Port for frontend")
@click.option("--no-frontend", is_flag=True, help="Don't start frontend")
@click.option("--open", "open_browser", is_flag=True, help="Open browser automatically")
@click.pass_context
def server(
    ctx: click.Context,
    host: str,
    port: int,
    frontend_port: int,
    no_frontend: bool,
    open_browser: bool,
) -> None:
    """Start the web dashboard server."""
    import uvicorn
    import webbrowser
    import threading
    import time

    config: Config = ctx.obj["config"]

    click.echo(f"\n🚀 Starting Cinder Dashboard...")
    click.echo(f"   API Server: http://{host}:{port}")
    if not no_frontend:
        click.echo(f"   Frontend: http://{host}:{frontend_port}")

    if open_browser:
        url = f"http://{host}:{frontend_port}" if not no_frontend else f"http://{host}:{port}/docs"
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()

    from cinder_cli.web.server import create_app

    app = create_app(config)

    uvicorn.run(app, host=host, port=port, log_level="info")


def main() -> None:
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()
