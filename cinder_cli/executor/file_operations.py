"""
File Operations - Safe file system operations.
"""

from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from rich.console import Console

from cinder_cli.config import Config

console = Console()


class FileOperations:
    """Provides safe file system operations."""

    ALLOWED_EXTENSIONS = {
        ".py",
        ".js",
        ".ts",
        ".html",
        ".css",
        ".json",
        ".yaml",
        ".yml",
        ".md",
        ".txt",
        ".sh",
    }

    def __init__(self, config: Config, working_dir: Path | None = None):
        self.config = config
        self.working_dir = working_dir or Path.cwd()
        self.backup_dir = self.working_dir / ".cinder_backups"
        self.backup_dir.mkdir(exist_ok=True)

    def create_file(
        self,
        file_path: str,
        content: str,
        backup: bool = True,
    ) -> dict[str, Any]:
        """
        Create a new file.

        Args:
            file_path: Path to the file
            content: File content
            backup: Whether to create backup if file exists

        Returns:
            Result with status and metadata
        """
        path = self._validate_path(file_path)

        # Check if file already exists
        if path.exists():
            if backup:
                self._create_backup(path)
            console.print(f"[yellow]文件已存在，将覆盖: {file_path}[/yellow]")

        # Create parent directories
        path.parent.mkdir(parents=True, exist_ok=True)

        # Write file
        path.write_text(content, encoding="utf-8")

        console.print(f"[green]✓ 创建文件: {file_path}[/green]")

        return {
            "status": "success",
            "file_path": str(path),
            "size": len(content),
            "created_at": datetime.now().isoformat(),
        }

    def create_directory(self, dir_path: str) -> dict[str, Any]:
        """
        Create a directory.

        Args:
            dir_path: Path to the directory

        Returns:
            Result with status
        """
        path = self._validate_path(dir_path)
        path.mkdir(parents=True, exist_ok=True)

        console.print(f"[green]✓ 创建目录: {dir_path}[/green]")

        return {
            "status": "success",
            "dir_path": str(path),
            "created_at": datetime.now().isoformat(),
        }

    def modify_file(
        self,
        file_path: str,
        content: str,
        backup: bool = True,
    ) -> dict[str, Any]:
        """
        Modify an existing file.

        Args:
            file_path: Path to the file
            content: New content
            backup: Whether to create backup

        Returns:
            Result with status
        """
        path = self._validate_path(file_path)

        if not path.exists():
            return {
                "status": "error",
                "message": f"文件不存在: {file_path}",
            }

        if backup:
            self._create_backup(path)

        path.write_text(content, encoding="utf-8")

        console.print(f"[green]✓ 修改文件: {file_path}[/green]")

        return {
            "status": "success",
            "file_path": str(path),
            "modified_at": datetime.now().isoformat(),
        }

    def delete_file(self, file_path: str, backup: bool = True) -> dict[str, Any]:
        """
        Delete a file.

        Args:
            file_path: Path to the file
            backup: Whether to create backup before deletion

        Returns:
            Result with status
        """
        path = self._validate_path(file_path)

        if not path.exists():
            return {
                "status": "error",
                "message": f"文件不存在: {file_path}",
            }

        if backup:
            self._create_backup(path)

        path.unlink()

        console.print(f"[green]✓ 删除文件: {file_path}[/green]")

        return {
            "status": "success",
            "file_path": str(path),
            "deleted_at": datetime.now().isoformat(),
        }

    def _validate_path(self, file_path: str) -> Path:
        """Validate file path for security."""
        path = Path(file_path)

        # Resolve to absolute path
        if not path.is_absolute():
            path = self.working_dir / path

        # Check if path is within working directory
        try:
            path.resolve().relative_to(self.working_dir.resolve())
        except ValueError:
            raise ValueError(f"路径不在工作目录内: {file_path}")

        # Check file extension
        if path.suffix and path.suffix not in self.ALLOWED_EXTENSIONS:
            raise ValueError(f"不允许的文件类型: {path.suffix}")

        return path

    def _create_backup(self, path: Path) -> Path:
        """Create backup of a file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{path.name}.{timestamp}.bak"
        backup_path = self.backup_dir / backup_name

        shutil.copy2(path, backup_path)

        console.print(f"[dim]备份: {backup_path}[/dim]")

        return backup_path

    def restore_backup(self, backup_path: str) -> dict[str, Any]:
        """
        Restore a file from backup.

        Args:
            backup_path: Path to the backup file

        Returns:
            Result with status
        """
        backup = Path(backup_path)

        if not backup.exists():
            return {
                "status": "error",
                "message": f"备份文件不存在: {backup_path}",
            }

        original_name = backup.name.split(".")[0]
        for ext in self.ALLOWED_EXTENSIONS:
            if backup.name.endswith(f"{ext}.*.bak"):
                original_name = backup.name.split(".")[0] + ext
                break

        original_path = backup.parent.parent / original_name

        shutil.copy2(backup, original_path)

        console.print(f"[green]✓ 恢复备份: {backup_path} -> {original_path}[/green]")

        return {
            "status": "success",
            "backup_path": str(backup),
            "restored_to": str(original_path),
            "restored_at": datetime.now().isoformat(),
        }

    def list_backups(self) -> list[dict[str, Any]]:
        """
        List all available backups.

        Returns:
            List of backup information
        """
        backups = []

        for backup_file in sorted(self.backup_dir.glob("*.bak"), reverse=True):
            stat = backup_file.stat()
            backups.append({
                "path": str(backup_file),
                "name": backup_file.name,
                "size": stat.st_size,
                "created_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            })

        return backups

    def rollback_operations(self, operations: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Rollback a list of operations.

        Args:
            operations: List of operations to rollback (in reverse order)

        Returns:
            Rollback result
        """
        results = []
        errors = []

        for op in reversed(operations):
            try:
                if op["type"] == "create_file":
                    path = Path(op["file_path"])
                    if path.exists():
                        path.unlink()
                        results.append({"action": "deleted", "path": str(path)})

                elif op["type"] == "create_directory":
                    path = Path(op["dir_path"])
                    if path.exists() and not any(path.iterdir()):
                        path.rmdir()
                        results.append({"action": "removed_dir", "path": str(path)})

                elif op["type"] == "modify_file":
                    backups = self.list_backups()
                    file_backups = [b for b in backups if op["file_path"].split("/")[-1].split(".")[0] in b["name"]]
                    if file_backups:
                        restore_result = self.restore_backup(file_backups[0]["path"])
                        results.append(restore_result)

                elif op["type"] == "delete_file":
                    backups = self.list_backups()
                    file_backups = [b for b in backups if op["file_path"].split("/")[-1].split(".")[0] in b["name"]]
                    if file_backups:
                        restore_result = self.restore_backup(file_backups[0]["path"])
                        results.append(restore_result)

            except Exception as e:
                errors.append({
                    "operation": op,
                    "error": str(e),
                })

        console.print(f"[yellow]回滚完成: {len(results)} 成功, {len(errors)} 失败[/yellow]")

        return {
            "status": "success" if not errors else "partial",
            "rolled_back": len(results),
            "errors": len(errors),
            "results": results,
            "error_details": errors,
        }
