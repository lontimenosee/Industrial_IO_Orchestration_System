import flet as ft


# ============================================================
# 1. 六个主页面的基础信息
# ============================================================

PAGE_INFO = [
    {
        "name": "系统总览",
        "subtitle": "当前批次及系统处理状态",
        "icon": ft.Icons.HOME_OUTLINED,
        "selected_icon": ft.Icons.HOME,
    },
    {
        "name": "CAD测点识别",
        "subtitle": "上传CAD图纸并提取测点信息",
        "icon": ft.Icons.SEARCH,
        "selected_icon": ft.Icons.SEARCH,
    },
    {
        "name": "信号类型识别",
        "subtitle": "识别I/O信号类型并确定目标Sheet",
        "icon": ft.Icons.TUNE,
        "selected_icon": ft.Icons.TUNE,
    },
    {
        "name": "增量通道分配",
        "subtitle": "在保护已有点位的前提下分配新增通道",
        "icon": ft.Icons.ACCOUNT_TREE_OUTLINED,
        "selected_icon": ft.Icons.ACCOUNT_TREE,
    },
    {
        "name": "冗余容量校验",
        "subtitle": "校验卡件20%冗余及容量状态",
        "icon": ft.Icons.FACT_CHECK_OUTLINED,
        "selected_icon": ft.Icons.FACT_CHECK,
    },
    {
        "name": "结果输出报告",
        "subtitle": "查看处理结果并导出Excel或PDF报告",
        "icon": ft.Icons.DESCRIPTION_OUTLINED,
        "selected_icon": ft.Icons.DESCRIPTION,
    },
]


# ============================================================
# 2. Flet程序入口
# ============================================================

def main(page: ft.Page):

    # -------------------------
    # 整个桌面窗口初始化
    # -------------------------
    page.title = "CAD测点表自动识别与Excel I/O点表增量生成系统"

    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#F5F7FA"
    page.padding = 0

    # 桌面窗口尺寸
    page.window.width = 1440
    page.window.height = 900
    page.window.min_width = 1100
    page.window.min_height = 700

    # -------------------------
    # 当前页面标题
    # -------------------------
    breadcrumb = ft.Text(
        "系统  >  系统总览",
        size=12,
        color="#7B8798",
    )

    page_title = ft.Text(
        "系统总览",
        size=26,
        weight=ft.FontWeight.BOLD,
        color="#253858",
    )

    page_subtitle = ft.Text(
        "当前批次及系统处理状态",
        size=13,
        color="#7B8798",
    )

    # -------------------------
    # 临时页面内容
    #
    # 以后真正的6个页面都会替换这里
    # -------------------------
    content_placeholder = ft.Container(
        expand=True,
        bgcolor="#FFFFFF",
        border=ft.Border.all(
            width=1,
            color="#E3E8EF",
        ),
        border_radius=8,
        padding=24,
        content=ft.Column(
            controls=[
                ft.Text(
                    "页面内容区域",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color="#253858",
                ),
                ft.Text(
                    "下一步我们会先在这里实现“系统总览”界面。",
                    color="#7B8798",
                ),
            ],
        ),
    )

    # -------------------------
    # 页面右侧主体，把标题、子标题和内容区域放在一起
    # -------------------------
    content_area = ft.Container(
        expand=True,
        padding=20,
        content=ft.Column(
            expand=True,
            spacing=6,
            controls=[
                breadcrumb,
                page_title,
                page_subtitle,
                ft.Container(height=10),
                content_placeholder,
            ],
        ),
    )

    # ========================================================
    # 3. 页面切换事件
    # ========================================================

    def change_page(e):
        """
        当用户点击左侧页面选择栏时执行。
        """

        index = e.control.selected_index

        info = PAGE_INFO[index]

        # 修改标题
        breadcrumb.value = f"系统  >  {info['name']}"
        page_title.value = info["name"]
        page_subtitle.value = info["subtitle"]

        # 目前只是用于观察页面切换
        content_placeholder.content = ft.Column(
            controls=[
                ft.Text(
                    info["name"],
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color="#253858",
                ),
                ft.Text(
                    f"这里以后实现：{info['subtitle']}",
                    color="#7B8798",
                ),
            ]
        )

        # 类似Qt修改控件以后刷新
        page.update()

    # ========================================================
    # 4. 可折叠页面选择栏
    # ========================================================

    navigation_rail = ft.NavigationRail(
        selected_index=0,

        # 默认展开
        extended=True,

        # expanded=True 时必须使用 NONE
        label_type=ft.NavigationRailLabelType.NONE,
        
        selected_label_text_style=ft.TextStyle(
            size=14,
            color="#253858",
            weight=ft.FontWeight.BOLD,
        ),

        unselected_label_text_style=ft.TextStyle(
            size=14,
            color="#7B8798",
        ),

        # 折叠宽度
        min_width=72,

        # 展开宽度
        min_extended_width=220,

        bgcolor="#FFFFFF",

        # 被选中页面的浅蓝色背景
        indicator_color="#E9F2FF",

        use_indicator=True,

        group_alignment=-1.0,

        on_change=change_page,

        destinations=[
            ft.NavigationRailDestination(
                icon=item["icon"],
                selected_icon=item["selected_icon"],
                label=item["name"],
            )
            # python 列表推导式，遍历 PAGE_INFO 列表，为每个页面创建一个 NavigationRailDestination
            for item in PAGE_INFO
        ],
    )

    # -------------------------
    # 折叠按钮
    # -------------------------

    def toggle_navigation(e):
        """
        展开 / 折叠页面选择栏。
        """

        navigation_rail.extended = not navigation_rail.extended

        if navigation_rail.extended:
            toggle_button.icon = ft.Icons.MENU_OPEN
        else:
            toggle_button.icon = ft.Icons.MENU

        page.update()

    toggle_button = ft.IconButton(
        icon=ft.Icons.MENU_OPEN,
        tooltip="展开 / 折叠菜单",
        on_click=toggle_navigation,
    )

    # 把按钮放到 NavigationRail 最上方
    navigation_rail.leading = ft.Container(
        padding=8,
        content=toggle_button,
    )

    # ========================================================
    # 5. 整个软件最外层布局
    # ========================================================

    app_shell = ft.Row(
        expand=True,
        spacing=0,
        controls=[
            navigation_rail,

            ft.VerticalDivider(
                width=1,
                thickness=1,
                color="#E3E8EF",
            ),

            content_area,
        ],
    )

    page.add(app_shell)


# ============================================================
# 6. 启动Flet桌面应用
# ============================================================

if __name__ == "__main__":
    ft.run(main)