"""Internationalization (i18n) module for Phone Agent UI messages."""

# Chinese messages
MESSAGES_ZH = {
    "thinking": "思考过程",
    "action": "执行动作",
    "task_completed": "任务完成",
    "done": "完成",
    "starting_task": "开始执行任务",
    "final_result": "最终结果",
    "task_result": "任务结果",
    "confirmation_required": "需要确认",
    "continue_prompt": "是否继续？(y/n)",
    "manual_operation_required": "需要人工操作",
    "manual_operation_hint": "请手动完成操作...",
    "press_enter_when_done": "完成后按回车继续",
    "connection_failed": "连接失败",
    "connection_successful": "连接成功",
    "step": "步骤",
    "task": "任务",
    "result": "结果",
}

# English messages
MESSAGES_EN = {
    "thinking": "Thinking",
    "action": "Action",
    "task_completed": "Task Completed",
    "done": "Done",
    "starting_task": "Starting task",
    "final_result": "Final Result",
    "task_result": "Task Result",
    "confirmation_required": "Confirmation Required",
    "continue_prompt": "Continue? (y/n)",
    "manual_operation_required": "Manual Operation Required",
    "manual_operation_hint": "Please complete the operation manually...",
    "press_enter_when_done": "Press Enter when done",
    "connection_failed": "Connection Failed",
    "connection_successful": "Connection Successful",
    "step": "Step",
    "task": "Task",
    "result": "Result",
}


def get_messages(lang: str = "cn") -> dict:
    """
    Get UI messages dictionary by language.

    Args:
        lang: Language code, 'cn' for Chinese, 'en' for English.

    Returns:
        Dictionary of UI messages.
    """
    if lang == "en":
        return MESSAGES_EN
    return MESSAGES_ZH


def get_message(key: str, lang: str = "cn") -> str:
    """
    Get a single UI message by key and language.

    Args:
        key: Message key.
        lang: Language code, 'cn' for Chinese, 'en' for English.

    Returns:
        Message string.
    """
    messages = get_messages(lang)
    return messages.get(key, key)
