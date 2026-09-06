"""Flet entry point for the Industrial I/O Orchestration System."""

from dataclasses import dataclass, field
from pathlib import Path

import flet as ft


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
    status: str = "等待配置"
    logs: list[str] = field(default_factory=lambda: ["等待选择 CAD/DXF 图纸与 Excel I/O 点表。"])

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


class IndustrialOrchestrationApp:
    """Flet desktop shell for the initial engineering dashboard and task view."""

    navy = "#102A43"
    blue = "#1479C9"
    surface = "#F4F7FB"
    muted = "#64748B"

    def __init__(self, page: ft.Page | None = None) -> None:
        self.page = page
        self.state = TaskState()
        self.adapter = BackendAdapter()
        self.current_view = "overview"
        self.content = ft.Container(expand=True)
        self.file_picker: ft.FilePicker | None = None

    def build_metric_card(self, label: str, value: str, accent: str) -> ft.Control:
        """Return one compact metric panel used by the dashboard."""
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(label, color=self.muted, size=13),
                    ft.Text(value, color=accent, size=27, weight=ft.FontWeight.BOLD),
                ],
                spacing=6,
            ),
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            padding=18,
            expand=True,
        )

    def build_overview(self) -> ft.Control:
        """Build the engineering dashboard view."""
        recent_logs = self.state.logs[-3:][::-1]
        return ft.Column(
            controls=[
                ft.Text("工程概览", size=28, weight=ft.FontWeight.BOLD, color=self.navy),
                ft.Text("工业图纸语义解析与 I/O 接口智能编排系统", color=self.muted),
                ft.Container(height=8),
                ft.Row(
                    controls=[
                        self.build_metric_card("当前任务状态", self.state.status, self.blue),
                        self.build_metric_card("待确认", "6", "#D97706"),
                        self.build_metric_card("容量风险", "2", "#DC2626"),
                        self.build_metric_card("业务接口", "待接入", "#7C3AED"),
                    ],
                    spacing=14,
                    wrap=True,
                ),
                ft.Container(height=8),
                ft.Row(
                    controls=[
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text("工程编排流程", size=18, weight=ft.FontWeight.BOLD, color=self.navy),
                                    ft.Text("01  图纸识别", color=self.muted),
                                    ft.Text("02  测点标准化与信号分类", color=self.muted),
                                    ft.Text("03  去重与 20% 冗余分配", color=self.muted),
                                    ft.Text("04  Excel 增量写入与差异报告", color=self.muted),
                                    ft.Button(
                                        "创建编排任务",
                                        bgcolor=self.blue,
                                        color=ft.Colors.WHITE,
                                        on_click=lambda _: self.navigate("orchestration"),
                                    ),
                                ],
                                spacing=13,
                            ),
                            bgcolor=ft.Colors.WHITE,
                            border_radius=12,
                            padding=20,
                            expand=2,
                        ),
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text("最近任务日志", size=18, weight=ft.FontWeight.BOLD, color=self.navy),
                                    *[
                                        ft.Container(
                                            content=ft.Text(log, color="#334155"),
                                            bgcolor="#F8FAFC",
                                            border_radius=8,
                                            padding=10,
                                        )
                                        for log in recent_logs
                                    ],
                                ],
                                spacing=10,
                            ),
                            bgcolor=ft.Colors.WHITE,
                            border_radius=12,
                            padding=20,
                            expand=3,
                        ),
                    ],
                    spacing=14,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    expand=True,
                ),
            ],
            spacing=10,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

    def build_file_input(
        self,
        label: str,
        path: str | None,
        kind: str,
        optional: bool = False,
    ) -> ft.Control:
        """Build one file-selection row without reading the selected file."""
        hint = "可选，后续用于规则配置" if optional else "尚未选择"
        filename = Path(path).name if path else hint
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Column(
                        controls=[
                            ft.Text(label, weight=ft.FontWeight.BOLD, color=self.navy),
                            ft.Text(filename, color=self.muted, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                        ],
                        spacing=4,
                        expand=True,
                    ),
                    ft.OutlinedButton("选择文件", on_click=lambda _: self.choose_file(kind)),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            padding=16,
        )

    def build_orchestration(self) -> ft.Control:
        """Build the task setup and safe preflight view."""
        return ft.Column(
            controls=[
                ft.Text("任务编排", size=28, weight=ft.FontWeight.BOLD, color=self.navy),
                ft.Text("选择工程输入后执行预检；本阶段不会读取或改写工程文件。", color=self.muted),
                ft.Container(height=8),
                self.build_file_input("CAD/DXF 图纸", self.state.cad_path, "cad"),
                self.build_file_input("Excel I/O 点表", self.state.excel_path, "excel"),
                self.build_file_input("规则配置文件", self.state.rules_path, "rules", optional=True),
                ft.Container(height=2),
                ft.Row(
                    controls=[
                        ft.Button("开始预检", bgcolor=self.blue, color=ft.Colors.WHITE, on_click=self.run_preflight),
                        ft.OutlinedButton("执行编排", on_click=self.run_orchestration),
                    ],
                    spacing=12,
                ),
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text("处理流程", size=17, weight=ft.FontWeight.BOLD, color=self.navy),
                            ft.Text("图纸识别  →  测点标准化  →  信号分类  →  去重  →  20% 冗余分配  →  增量写入", color="#334155"),
                            ft.Text("后端适配状态：接口预留，等待业务脚本接入。", color="#7C3AED"),
                        ],
                        spacing=10,
                    ),
                    bgcolor="#EEF5FC",
                    border_radius=10,
                    padding=18,
                ),
            ],
            spacing=14,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

    def build_sidebar(self) -> ft.Control:
        """Build the fixed navigation rail with future-function placeholders."""
        active_style = ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor="#1E5B8C")
        idle_style = ft.ButtonStyle(color="#D8E6F3")
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("INDUSTRIAL I/O", color=ft.Colors.WHITE, size=16, weight=ft.FontWeight.BOLD),
                    ft.Text("智能编排系统", color="#BBD6EE", size=12),
                    ft.Divider(color="#315271"),
                    ft.TextButton("工程概览", style=active_style if self.current_view == "overview" else idle_style, on_click=lambda _: self.navigate("overview")),
                    ft.TextButton("任务编排", style=active_style if self.current_view == "orchestration" else idle_style, on_click=lambda _: self.navigate("orchestration")),
                    ft.Divider(color="#315271"),
                    ft.Text("后续版本", color="#9FC2DF", size=12),
                    *[
                        ft.TextButton(label, style=idle_style, on_click=lambda _, item=label: self.show_future_notice(item))
                        for label in ("人工确认", "容量报告", "差异报告")
                    ],
                    ft.Container(expand=True),
                    ft.Text("GUI 原型 v0.1", color="#9FC2DF", size=12),
                ],
                spacing=7,
                expand=True,
            ),
            bgcolor=self.navy,
            width=210,
            padding=18,
        )

    def start(self) -> None:
        """Configure the live Flet page and render the initial dashboard."""
        if self.page is None:
            raise RuntimeError("启动 GUI 需要 Flet Page 实例。")
        self.page.title = "工业 I/O 接口智能编排系统"
        self.page.bgcolor = self.surface
        self.page.padding = 0
        self.page.window.width = 1280
        self.page.window.height = 820
        self.file_picker = ft.FilePicker()
        self.page.services.append(self.file_picker)
        self.render()

    def navigate(self, view: str) -> None:
        """Switch between the two implemented views."""
        self.current_view = view
        self.render()

    def render(self) -> None:
        """Refresh the page shell from the current in-memory state."""
        if self.page is None:
            return
        body = self.build_overview() if self.current_view == "overview" else self.build_orchestration()
        self.page.controls.clear()
        self.page.add(
            ft.Row(
                controls=[
                    self.build_sidebar(),
                    ft.Container(content=body, padding=28, expand=True),
                ],
                expand=True,
                spacing=0,
            )
        )
        self.page.update()

    def notify(self, message: str, error: bool = False) -> None:
        """Show a short in-app notification when a live page is available."""
        if self.page is not None:
            self.page.show_dialog(ft.SnackBar(message, bgcolor="#B42318" if error else self.navy))

    def run_preflight(self, _: object | None = None) -> None:
        """Run safe input validation and refresh the task status."""
        result = self.adapter.preflight(self.state)
        self.state.status = "预检通过（接口待接入）" if result.ok else "等待补充输入"
        self.state.logs.append(result.message)
        self.notify(result.message, error=not result.ok)
        self.render()

    def run_orchestration(self, _: object | None = None) -> None:
        """Report the intentionally unavailable business-operation boundary."""
        result = self.adapter.run_orchestration(self.state)
        self.state.logs.append(result.message)
        self.notify(result.message, error=True)
        self.render()

    def show_future_notice(self, label: str) -> None:
        """Explain that a planned page is outside the first two-view release."""
        self.notify(f"{label}将在后续版本开发，目前保留导航入口。")

    def choose_file(self, kind: str) -> None:
        """Schedule a native picker request without blocking Flet's UI thread."""
        if self.page is None or self.file_picker is None:
            self.notify("文件选择器尚未初始化，请在桌面应用中打开此页面。", error=True)
            return
        self.page.run_task(self.pick_file, kind)

    async def pick_file(self, kind: str) -> None:
        """Store a selected local path without inspecting the file contents."""
        if self.file_picker is None:
            return
        extensions = {
            "cad": ["dwg", "dxf"],
            "excel": ["xlsx", "xlsm", "xls"],
            "rules": ["json", "yaml", "yml"],
        }[kind]
        labels = {"cad": "CAD/DXF 图纸", "excel": "Excel I/O 点表", "rules": "规则配置文件"}
        try:
            files = await self.file_picker.pick_files(
                dialog_title=f"选择{labels[kind]}",
                file_type=ft.FilePickerFileType.CUSTOM,
                allowed_extensions=extensions,
                allow_multiple=False,
            )
        except Exception as exc:  # Flet platform services can be unavailable.
            self.notify(f"无法打开文件选择器：{exc}", error=True)
            return

        if not files:
            return
        selected_path = files[0].path or files[0].name
        setattr(self.state, f"{kind}_path", selected_path)
        self.state.logs.append(f"已选择{labels[kind]}：{Path(selected_path).name}")
        self.render()


def main(page: ft.Page) -> None:
    """Launch the initial two-page Flet desktop application."""
    app = IndustrialOrchestrationApp(page)
    app.start()


if __name__ == "__main__":
    ft.run(main)
