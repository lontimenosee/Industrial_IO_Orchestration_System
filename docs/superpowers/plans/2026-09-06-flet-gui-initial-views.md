# Flet GUI 初始双页面实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 `src/main_gui.py` 实现可启动的 Flet 工业控制台 GUI，交付工程概览与任务编排两个可交互页面。

**Architecture:** 单文件实现三个边界清晰的对象：不依赖 Flet 的 `TaskState` 保存任务状态，`BackendAdapter` 校验输入并返回“业务接口未接入”结果，`IndustrialOrchestrationApp` 仅负责 Flet 控件和页面事件。概览与任务编排都从同一状态对象重建，确保预检及日志变动后两个页面显示一致。

**Tech Stack:** Python 3.12.9、Flet 0.86.5、pytest。

**Spec:** `docs/superpowers/specs/2026-09-06-flet-gui-design.md`

## Global Constraints

- 只修改 `src/main_gui.py` 和 `test/test_gui.py`；不修改 README、现有空业务模块或用户输入文件。
- 初版只实现“工程概览”和“任务编排”两页；其余三项导航显示为后续版本入口。
- 不读取 CAD/Excel 内容，不写入、复制或导出任何工程文件。
- 所有未接入的业务动作均显示“接口预留，等待业务脚本接入”。
- 测试必须先失败，再编写满足测试的最小实现。

---

### Task 1: 创建可测试的任务状态与预检适配器

**Files:**
- Modify: `src/main_gui.py`
- Modify: `test/test_gui.py`

**Interfaces:**
- Produces: `TaskState(cad_path: str | None = None, excel_path: str | None = None, rules_path: str | None = None)`。
- Produces: `TaskState.missing_required_files() -> list[str]`，缺 CAD 时返回 `['CAD/DXF 图纸']`，缺 Excel 时返回 `['Excel I/O 点表']`。
- Produces: `BackendAdapter.preflight(state: TaskState) -> AdapterResult`，成功时 `ok=True` 且消息包含 `接口预留`；失败时 `ok=False` 且消息列出缺项。
- Produces: `BackendAdapter.run_orchestration(state: TaskState) -> AdapterResult`，始终返回 `ok=False` 和 `等待业务脚本接入`。

- [ ] **Step 1: 写入任务状态和预检的失败测试**

```python
from src.main_gui import BackendAdapter, TaskState


def test_preflight_names_both_missing_required_inputs():
    result = BackendAdapter().preflight(TaskState())

    assert not result.ok
    assert 'CAD/DXF 图纸' in result.message
    assert 'Excel I/O 点表' in result.message


def test_preflight_accepts_selected_cad_and_excel_without_reading_them():
    state = TaskState(cad_path='C:/project/drawing.dxf', excel_path='C:/project/io.xlsx')

    result = BackendAdapter().preflight(state)

    assert result.ok
    assert '接口预留' in result.message


def test_orchestration_is_explicitly_not_connected_to_business_scripts():
    result = BackendAdapter().run_orchestration(TaskState())

    assert not result.ok
    assert '等待业务脚本接入' in result.message
```

- [ ] **Step 2: 运行测试并确认因缺少导入对象而失败**

Run: `.venv\\Scripts\\python.exe -m pytest test/test_gui.py -v`

Expected: FAIL，提示无法从 `src.main_gui` 导入 `BackendAdapter` 或 `TaskState`。

- [ ] **Step 3: 实现最小状态模型和适配器**

```python
@dataclass
class AdapterResult:
    ok: bool
    message: str


@dataclass
class TaskState:
    cad_path: str | None = None
    excel_path: str | None = None
    rules_path: str | None = None

    def missing_required_files(self) -> list[str]:
        return [
            label
            for value, label in (
                (self.cad_path, 'CAD/DXF 图纸'),
                (self.excel_path, 'Excel I/O 点表'),
            )
            if not value
        ]
```

让 `BackendAdapter.preflight()` 基于 `missing_required_files()` 构造结果；让 `run_orchestration()` 返回固定、明确的未接入提示。不得访问文件系统。

- [ ] **Step 4: 运行测试并确认通过**

Run: `.venv\\Scripts\\python.exe -m pytest test/test_gui.py -v`

Expected: 3 passed。

- [ ] **Step 5: 提交任务状态与适配器**

```bash
git add src/main_gui.py test/test_gui.py
git commit -m "feat: add GUI task state adapter"
```

### Task 2: 实现概览和任务编排 Flet 页面

**Files:**
- Modify: `src/main_gui.py`
- Modify: `test/test_gui.py`

**Interfaces:**
- Consumes: `TaskState`、`BackendAdapter`、`AdapterResult`。
- Produces: `IndustrialOrchestrationApp(page: ft.Page)`，含 `build_overview() -> ft.Control`、`build_orchestration() -> ft.Control` 和 `navigate(route: str) -> None`。
- Produces: `main(page: ft.Page) -> None` 作为 Flet 启动入口。

- [ ] **Step 1: 写入视图和导航的失败测试**

```python
import flet as ft
from src.main_gui import IndustrialOrchestrationApp


def test_overview_contains_the_engineering_summary_title():
    app = IndustrialOrchestrationApp(ft.Page())

    overview = app.build_overview()

    assert overview is not None
    assert '工程概览' in str(overview)


def test_orchestration_view_displays_required_input_labels():
    app = IndustrialOrchestrationApp(ft.Page())

    view = app.build_orchestration()

    rendered = str(view)
    assert 'CAD/DXF 图纸' in rendered
    assert 'Excel I/O 点表' in rendered
```

- [ ] **Step 2: 运行测试并确认因应用类不存在而失败**

Run: `.venv\\Scripts\\python.exe -m pytest test/test_gui.py -v`

Expected: FAIL，提示无法从 `src.main_gui` 导入 `IndustrialOrchestrationApp`。

- [ ] **Step 3: 最小实现两页 UI 与交互**

```python
def build_metric_card(self, label: str, value: str, color: str) -> ft.Control:
    return ft.Container(
        content=ft.Column([ft.Text(label), ft.Text(value, size=26, weight=ft.FontWeight.BOLD)]),
        bgcolor=ft.Colors.WHITE,
        border_radius=12,
        padding=16,
        expand=True,
    )
```

实现：深蓝侧边栏、概览指标卡、任务流程卡和最近日志；任务编排页显示三个文件字段、三个“选择文件”按钮、预检与执行按钮。文件选择使用 Flet `FilePicker`；按钮回调仅更新 `TaskState`、刷新页面、显示 `SnackBar`。若 Flet 运行环境不支持文件选择，显示错误而保留页面可用。

实现三个后续入口按钮（人工确认、容量报告、差异报告），点击显示“后续版本开发中”。不实现这些页面。

- [ ] **Step 4: 运行测试并确认通过**

Run: `.venv\\Scripts\\python.exe -m pytest test/test_gui.py -v`

Expected: 5 passed。

- [ ] **Step 5: 进行无窗口导入校验和启动烟雾验证**

Run: `.venv\\Scripts\\python.exe -m py_compile src/main_gui.py`

Expected: exit code 0。

Run: `.venv\\Scripts\\python.exe src/main_gui.py`

Expected: Flet 桌面窗口打开，显示工程概览；关闭窗口后命令正常退出。

- [ ] **Step 6: 提交两页 Flet GUI**

```bash
git add src/main_gui.py test/test_gui.py
git commit -m "feat: build initial Flet GUI views"
```

## Plan Self-Review

- 规格范围已缩小到两个页面；Task 2 覆盖两个页面、导航入口、工业视觉和文件/预检交互。
- Task 1 覆盖无后端脚本时的输入验证和明确的未接入行为。
- 所有后端写入、解析和报告导出均明确排除，未留实现占位。
- 接口名称、参数和返回类型在两个任务间保持一致。
