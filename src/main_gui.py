"""Flet entry point for the Industrial I/O Orchestration System."""

from dataclasses import dataclass


@dataclass(frozen=True)
class AdapterResult:
    """Result returned by a future business-service adapter."""

    ok: bool
    message: str


@dataclass
class TaskState:
    """In-memory input state for one orchestration task."""

    cad_path: str | None = None
    excel_path: str | None = None
    rules_path: str | None = None

    def missing_required_files(self) -> list[str]:
        """Return labels for required inputs that have not been selected."""
        return [
            label
            for value, label in (
                (self.cad_path, "CAD/DXF 图纸"),
                (self.excel_path, "Excel I/O 点表"),
            )
            if not value
        ]


class BackendAdapter:
    """Safe placeholder for CAD, rule, allocation, and Excel services."""

    def preflight(self, state: TaskState) -> AdapterResult:
        """Validate the selected inputs without opening or changing files."""
        missing = state.missing_required_files()
        if missing:
            return AdapterResult(False, f"请先选择：{'、'.join(missing)}")
        return AdapterResult(True, "预检通过：业务接口预留，尚未读取工程文件。")

    def run_orchestration(self, state: TaskState) -> AdapterResult:
        """State the intentional boundary of the first GUI iteration."""
        return AdapterResult(False, "接口预留，等待业务脚本接入后执行编排。")
