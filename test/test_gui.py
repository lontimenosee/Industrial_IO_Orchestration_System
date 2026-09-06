from src.main_gui import BackendAdapter, TaskState


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
