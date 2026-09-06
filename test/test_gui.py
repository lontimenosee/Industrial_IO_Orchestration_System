from src.main_gui import BackendAdapter, TaskState


def visible_text_values(control):
    values = []
    value = getattr(control, "value", None)
    if isinstance(value, str):
        values.append(value)

    content = getattr(control, "content", None)
    if isinstance(content, str):
        values.append(content)
    elif content is not None:
        values.extend(visible_text_values(content))

    for child in getattr(control, "controls", []) or []:
        values.extend(visible_text_values(child))
    return values


def test_preflight_names_both_missing_required_inputs():
    result = BackendAdapter().preflight(TaskState())

    assert not result.ok
    assert "CAD/DXF 图纸" in result.message
    assert "Excel I/O 点表" in result.message


def test_preflight_accepts_selected_cad_and_excel_without_reading_them():
    state = TaskState(
        cad_path="C:/project/drawing.dxf",
        excel_path="C:/project/io.xlsx",
    )

    result = BackendAdapter().preflight(state)

    assert result.ok
    assert "接口预留" in result.message


def test_orchestration_is_explicitly_not_connected_to_business_scripts():
    result = BackendAdapter().run_orchestration(TaskState())

    assert not result.ok
    assert "等待业务脚本接入" in result.message


def test_overview_view_exposes_the_engineering_dashboard_summary():
    from src.main_gui import IndustrialOrchestrationApp

    view = IndustrialOrchestrationApp().build_overview()

    text = " ".join(visible_text_values(view))
    assert "工程概览" in text
    assert "当前任务状态" in text
    assert "待确认" in text


def test_orchestration_view_exposes_required_inputs_and_preflight_action():
    from src.main_gui import IndustrialOrchestrationApp

    view = IndustrialOrchestrationApp().build_orchestration()

    text = " ".join(visible_text_values(view))
    assert "CAD/DXF 图纸" in text
    assert "Excel I/O 点表" in text
    assert "开始预检" in text
