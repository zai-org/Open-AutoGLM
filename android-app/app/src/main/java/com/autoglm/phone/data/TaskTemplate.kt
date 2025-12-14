package com.autoglm.phone.data

/**
 * Task template data model.
 */
data class TaskTemplate(
    val id: String,
    val title: String,
    val description: String,
    val icon: String,       // Emoji icon
    val category: String,
    val prompt: String,     // The actual task prompt to execute
    val isBuiltIn: Boolean = true
)

/**
 * Task template categories.
 */
object TemplateCategories {
    const val GAME = "游戏助手"
    const val SOCIAL = "社交娱乐"
    const val SHOPPING = "电商购物"
    const val WORK = "工作效率"
    const val LIFE = "生活服务"
    const val INFO = "信息获取"
}

/**
 * Built-in task templates.
 */
object BuiltInTemplates {
    
    val all: List<TaskTemplate> = listOf(
        // 游戏助手
        TaskTemplate(
            id = "xxl_checkin",
            title = "开心消消乐签到",
            description = "完成每日签到领取奖励",
            icon = "🎮",
            category = TemplateCategories.GAME,
            prompt = "打开开心消消乐，完成每日签到，领取签到奖励"
        ),
        TaskTemplate(
            id = "xxl_daily",
            title = "开心消消乐日常",
            description = "完成每日任务领取奖励",
            icon = "⭐",
            category = TemplateCategories.GAME,
            prompt = "打开开心消消乐，查看每日任务，领取已完成的任务奖励"
        ),
        TaskTemplate(
            id = "xxl_play",
            title = "开心消消乐过关",
            description = "自动进入关卡尝试过关",
            icon = "🎯",
            category = TemplateCategories.GAME,
            prompt = "打开开心消消乐，进入当前关卡，自动进行消除操作尝试过关。观察屏幕上相同颜色的消除块，点击可以消除的位置"
        ),
        TaskTemplate(
            id = "xxl_ads",
            title = "消消乐看广告",
            description = "看广告获取体力或金币",
            icon = "📺",
            category = TemplateCategories.GAME,
            prompt = "打开开心消消乐，找到可以看广告获取奖励的入口，观看一个广告领取奖励"
        ),
        TaskTemplate(
            id = "wzry_checkin",
            title = "王者荣耀签到",
            description = "完成每日签到领取奖励",
            icon = "⚔️",
            category = TemplateCategories.GAME,
            prompt = "打开王者荣耀，进入活动中心，完成每日签到"
        ),
        TaskTemplate(
            id = "genshin_checkin",
            title = "原神签到",
            description = "领取原神每日奖励",
            icon = "🌟",
            category = TemplateCategories.GAME,
            prompt = "打开原神，进入邮箱领取奖励，然后到纪行领取每日奖励"
        ),
        
        // 社交娱乐
        TaskTemplate(
            id = "douyin_scroll",
            title = "自动刷抖音",
            description = "自动滑动浏览短视频",
            icon = "🎬",
            category = TemplateCategories.SOCIAL,
            prompt = "打开抖音，帮我自动刷10个短视频，每个视频看3秒后向上滑动"
        ),
        TaskTemplate(
            id = "douyin_like",
            title = "刷视频+点赞",
            description = "刷视频并自动点赞喜欢的内容",
            icon = "❤️",
            category = TemplateCategories.SOCIAL,
            prompt = "打开抖音极速版，帮我刷20个视频，如果视频有趣就点赞"
        ),
        TaskTemplate(
            id = "wechat_moments_like",
            title = "朋友圈点赞",
            description = "自动给朋友圈点赞",
            icon = "👍",
            category = TemplateCategories.SOCIAL,
            prompt = "打开微信，进入朋友圈，给最近5条朋友圈点赞"
        ),
        TaskTemplate(
            id = "xiaohongshu_browse",
            title = "浏览小红书",
            description = "自动浏览小红书笔记",
            icon = "📕",
            category = TemplateCategories.SOCIAL,
            prompt = "打开小红书，浏览推荐页面的10条笔记"
        ),
        
        // 电商购物
        TaskTemplate(
            id = "taobao_checkin",
            title = "淘宝签到",
            description = "领取淘宝每日签到奖励",
            icon = "🛒",
            category = TemplateCategories.SHOPPING,
            prompt = "打开淘宝，找到签到入口并完成今日签到"
        ),
        TaskTemplate(
            id = "jd_checkin",
            title = "京东签到",
            description = "完成京东每日签到",
            icon = "🏪",
            category = TemplateCategories.SHOPPING,
            prompt = "打开京东，找到签到入口完成每日签到领取京豆"
        ),
        TaskTemplate(
            id = "meituan_coupon",
            title = "美团领券",
            description = "领取美团优惠券",
            icon = "🎫",
            category = TemplateCategories.SHOPPING,
            prompt = "打开美团，进入领券中心，领取可用的优惠券"
        ),
        
        // 工作效率
        TaskTemplate(
            id = "wechat_reply",
            title = "查看微信消息",
            description = "查看未读微信消息",
            icon = "💬",
            category = TemplateCategories.WORK,
            prompt = "打开微信，查看是否有未读消息，告诉我有哪些人发来了消息"
        ),
        TaskTemplate(
            id = "clear_notifications",
            title = "清理通知",
            description = "清理手机通知栏",
            icon = "🧹",
            category = TemplateCategories.WORK,
            prompt = "下拉通知栏，清除所有通知"
        ),
        
        // 生活服务
        TaskTemplate(
            id = "check_weather",
            title = "查看天气",
            description = "查看今日天气预报",
            icon = "☀️",
            category = TemplateCategories.LIFE,
            prompt = "打开天气应用，告诉我今天的天气情况和温度"
        ),
        TaskTemplate(
            id = "alipay_checkin",
            title = "支付宝签到",
            description = "完成支付宝蚂蚁庄园喂鸡",
            icon = "🐔",
            category = TemplateCategories.LIFE,
            prompt = "打开支付宝，进入蚂蚁庄园，给小鸡喂食"
        ),
        
        // 信息获取
        TaskTemplate(
            id = "news_headlines",
            title = "今日要闻",
            description = "浏览今日热点新闻",
            icon = "📰",
            category = TemplateCategories.INFO,
            prompt = "打开今日头条，浏览首页推荐的5条新闻标题"
        ),
        TaskTemplate(
            id = "weibo_trending",
            title = "微博热搜",
            description = "查看微博热搜榜",
            icon = "🔥",
            category = TemplateCategories.INFO,
            prompt = "打开微博，查看热搜榜前10条"
        )
    )
    
    fun getByCategory(category: String): List<TaskTemplate> {
        return all.filter { it.category == category }
    }
    
    fun getCategories(): List<String> {
        return all.map { it.category }.distinct()
    }
}
