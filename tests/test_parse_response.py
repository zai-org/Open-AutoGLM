from phone_agent.model.client import parse_response


def test_parse_response() -> None:
    content = """<think>先思考</think>
<answer>
do(action="Launch", app="知乎")
</answer>"""
    thinking, action = parse_response(content)
    assert thinking == "先思考"
    assert action == 'do(action="Launch", app="知乎")'

    content = """<think>用户需要打开知乎查看首页第一条消息，当前在系统桌面，首先需要启动知乎应用，因此执行Launch操作打开知乎。</think>
<answer>
do(action="Launch", app="知乎")
</answer>"""
    thinking, action = parse_response(content)
    assert (
        thinking
        == "用户需要打开知乎查看首页第一条消息，当前在系统桌面，首先需要启动知乎应用，因此执行Launch操作打开知乎。"
    )
    assert action == 'do(action="Launch", app="知乎")'

    content = '先总结一下\nfinish(message="任务完成")'
    thinking, action = parse_response(content)
    assert thinking == "先总结一下"
    assert action == 'finish(message="任务完成")'

    content = '先分析页面元素\ndo(action="Tap", element=[120,240])'
    thinking, action = parse_response(content)
    assert thinking == "先分析页面元素"
    assert action == 'do(action="Tap", element=[120,240])'

    content = '直接输出动作 do(action="Back")'
    thinking, action = parse_response(content)
    assert thinking == "直接输出动作"
    assert action == 'do(action="Back")'

    content = "这是一段没有动作标记的普通文本"
    thinking, action = parse_response(content)
    assert thinking == ""
    assert action == content

    content = """<think>先思考</think>
<answer>
do(action="Launch", app="知乎")"""
    thinking, action = parse_response(content)
    assert thinking == "<think>先思考</think>\n<answer>"
    assert action == 'do(action="Launch", app="知乎")'
