# Flet 简单教程

本教程面向 Python 初学者，使用本项目当前的 Flet 0.86.5 环境说明如何理解和扩展桌面界面。

## 1. Flet 是什么

Flet 是一个 Python UI 框架：使用 Python 创建按钮、文本、表格和布局控件，再由 Flet 渲染成桌面或 Web 应用。它适合本项目的原因是后续 CAD 解析、规则处理与 Excel 脚本都能继续使用 Python，无需再维护独立的前端语言和服务。

当前项目的入口位于 `src/main_gui.py`：

```python
if __name__ == "__main__":
    ft.run(main)
```

`ft.run(main)` 启动 Flet；框架创建窗口后会调用 `main(page)`。`page` 代表当前应用窗口。

## 2. 最小可运行示例

在项目目录新建 `hello_flet.py`，填写：

```python
import flet as ft


def main(page: ft.Page) -> None:
    page.title = "Flet 入门"
    page.add(
        ft.Column(
            controls=[
                ft.Text("你好，工业 I/O 系统", size=24),
                ft.Button(
                    "显示提示",
                    on_click=lambda _: page.show_dialog(ft.SnackBar("按钮已点击")),
                ),
            ]
        )
    )


ft.run(main)
```

运行：

```powershell
.\.venv\Scripts\python.exe .\hello_flet.py
```

会打开一个窗口，点击按钮会显示提示条。示例中的 `ft.Text`、`ft.Button`、`ft.Column` 都是控件；`page.add()` 把控件添加到窗口。

## 3. 常用布局控件

| 控件 | 用途 | 当前项目中的例子 |
| --- | --- | --- |
| `ft.Column` | 从上到下排列控件 | 概览页标题、指标卡和日志区 |
| `ft.Row` | 从左到右排列控件 | 四张指标卡、侧栏与主内容区 |
| `ft.Container` | 设置背景、圆角、间距、内边距 | 白色卡片、深蓝色侧栏 |
| `ft.Text` | 显示文本 | 页面标题、文件名、日志 |
| `ft.Button` | 主操作按钮 | “创建编排任务”“开始预检” |
| `ft.OutlinedButton` | 次要操作按钮 | “选择文件”“执行编排” |

例如，下面的卡片具有白色背景、圆角和内边距：

```python
card = ft.Container(
    content=ft.Text("容量风险：2"),
    bgcolor=ft.Colors.WHITE,
    border_radius=12,
    padding=18,
)
```

## 4. 状态：让页面记住用户操作

Flet 控件负责显示，Python 对象负责保存状态。本项目用 `TaskState` 保存用户选中的文件路径、任务状态和日志：

```python
@dataclass
class TaskState:
    cad_path: str | None = None
    excel_path: str | None = None
    rules_path: str | None = None
    status: str = "等待配置"
    logs: list[str] = field(default_factory=list)
```

用户点击“开始预检”时，`run_preflight()` 调用 `BackendAdapter.preflight()`，更新 `state.status` 与 `state.logs`，再调用 `render()` 重建页面。这样概览页与任务编排页显示的是同一份任务状态。

初学时可以记住这个模式：

```text
事件发生 → 更新 Python 状态 → 重新渲染控件
```

## 5. 事件处理

按钮的 `on_click` 接收一个事件参数。若不需要读取事件内容，可用 `_` 忽略它：

```python
ft.Button(
    "开始预检",
    on_click=lambda _: self.run_preflight(),
)
```

项目中也可以直接传入兼容的处理函数：

```python
ft.Button("开始预检", on_click=self.run_preflight)
```

`run_preflight()` 的可选参数用于接收 Flet 传入的点击事件：

```python
def run_preflight(self, _: object | None = None) -> None:
    result = self.adapter.preflight(self.state)
    self.state.status = "预检通过（接口待接入）" if result.ok else "等待补充输入"
    self.render()
```

## 6. 文件选择器与异步函数

文件选择器需要等待用户关闭系统对话框，因此 `pick_file()` 是异步函数：

```python
async def pick_file(self, kind: str) -> None:
    files = await self.file_picker.pick_files(
        file_type=ft.FilePickerFileType.CUSTOM,
        allowed_extensions=["dxf", "dwg"],
        allow_multiple=False,
    )
    if files:
        self.state.cad_path = files[0].path or files[0].name
        self.render()
```

不要在点击回调中直接阻塞等待文件选择；项目使用 `page.run_task(self.pick_file, kind)` 在 Flet 的任务机制中执行协程。当前版本只保存路径，不打开或解析文件。

## 7. 如何新增一个页面

以未来“容量报告”为例，可按以下顺序扩展：

1. 在 `IndustrialOrchestrationApp` 中新增 `build_capacity_report()`，返回一个 `ft.Column` 或 `ft.Container`。
2. 在 `build_sidebar()` 中将“容量报告”按钮改为 `self.navigate("capacity")`。
3. 在 `render()` 中按 `current_view` 选择 `build_capacity_report()`。
4. 给 `TaskState` 或后续 `BackendAdapter` 增加容量数据字段与获取方法。
5. 在 `test/test_gui.py` 中先添加失败测试，确认页面包含“总通道”“80% 上限”“使用率”等关键字段，再编写页面代码。

建议先将页面数据写成固定样例，待通道分配脚本稳定后，再通过 `BackendAdapter` 替换为真实数据。

## 8. 与后端脚本对接的边界

GUI 不应直接把 Excel 写入逻辑塞进按钮事件中。项目预留的 `BackendAdapter` 是 UI 与业务脚本之间的边界：

```text
GUI 事件
  → BackendAdapter
  → CAD 解析 / 规则引擎 / 通道分配 / Excel 导出脚本
  → 结构化结果
  → GUI 展示状态、日志、报告
```

接入后端时，优先让适配器返回结构化数据或结果对象；UI 只负责调用、显示进度和处理错误。这样可以独立测试业务规则和界面，避免工程文件操作与控件代码互相耦合。

## 9. 调试与测试命令

启动 GUI：

```powershell
.\.venv\Scripts\python.exe .\src\main_gui.py
```

运行测试：

```powershell
.\.venv\Scripts\python.exe -m pytest test -v
```

检查 Python 语法：

```powershell
.\.venv\Scripts\python.exe -m py_compile .\src\main_gui.py
```

常见问题：

- `No module named flet`：确认使用的是 `.venv\\Scripts\\python.exe`，并执行 `.\.venv\Scripts\python.exe -m pip install flet`。
- 文件选择框未弹出：检查是否在桌面窗口中运行；当前文件选择器不适用于无图形界面的终端环境。
- 界面没有刷新：确认状态更新后调用了 `render()` 或对已添加控件调用了 `page.update()`。
- 点击“执行编排”没有生成 Excel：这是当前版本的预期行为，业务脚本尚未接入。
