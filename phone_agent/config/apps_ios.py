"""iOS App Bundle ID mappings.

This file contains the mapping between app names (Chinese/English)
and their iOS bundle identifiers for app launching.
"""

# iOS App Bundle ID mappings
# Format: {"App中文名": "bundle.id", "AppEnglishName": "bundle.id"}
IOS_APP_PACKAGES = {
    # ===== 社交 Social =====
    "微信": "com.tencent.xin",
    "WeChat": "com.tencent.xin",
    "QQ": "com.tencent.mqq",
    "微博": "com.sina.weibo",
    "Weibo": "com.sina.weibo",
    "钉钉": "com.laiwang.DingTalk",
    "DingTalk": "com.laiwang.DingTalk",
    "飞书": "com.bytedance.lark",
    "Lark": "com.bytedance.lark",
    "企业微信": "com.tencent.wework",
    "WeCom": "com.tencent.wework",
    
    # ===== 购物 Shopping =====
    "淘宝": "com.taobao.taobao4iphone",
    "Taobao": "com.taobao.taobao4iphone",
    "京东": "com.360buy.jdmobile",
    "JD": "com.360buy.jdmobile",
    "拼多多": "com.xunmeng.pinduoduo",
    "Pinduoduo": "com.xunmeng.pinduoduo",
    "闲鱼": "com.taobao.fleamarket",
    "Xianyu": "com.taobao.fleamarket",
    "天猫": "com.tmall.tmall",
    "Tmall": "com.tmall.tmall",
    "唯品会": "com.vipshop.iphone",
    "Vipshop": "com.vipshop.iphone",
    "苏宁易购": "com.suning.SuningEBuy",
    "Suning": "com.suning.SuningEBuy",
    "小米商城": "com.xiaomi.mishop",
    "得物": "com.shizhuang.duapp",
    "Dewu": "com.shizhuang.duapp",
    
    # ===== 外卖/生活服务 Food Delivery / Life Services =====
    "美团": "com.meituan.imeituan",
    "Meituan": "com.meituan.imeituan",
    "饿了么": "me.ele.ios.eleme",
    "Eleme": "me.ele.ios.eleme",
    "大众点评": "com.dianping.dpscope",
    "Dianping": "com.dianping.dpscope",
    "盒马": "com.wdk.hema",
    "Hema": "com.wdk.hema",
    "叮咚买菜": "com.ddmc.DDMC",
    "每日优鲜": "com.missfresh.clients",
    
    # ===== 出行 Transportation =====
    "高德地图": "com.autonavi.amap",
    "Amap": "com.autonavi.amap",
    "百度地图": "com.baidu.map",
    "Baidu Map": "com.baidu.map",
    "滴滴出行": "com.sdu.didi.gsui",
    "Didi": "com.sdu.didi.gsui",
    "携程": "com.ctrip.iphone",
    "Ctrip": "com.ctrip.iphone",
    "飞猪": "com.taobao.travel",
    "Fliggy": "com.taobao.travel",
    "铁路12306": "com.MobileTicket",
    "12306": "com.MobileTicket",
    "哈啰": "com.jingyao.Hellobike",
    "Hellobike": "com.jingyao.Hellobike",
    
    # ===== 内容/娱乐 Content / Entertainment =====
    "小红书": "com.xingin.discover",
    "Xiaohongshu": "com.xingin.discover",
    "RED": "com.xingin.discover",
    "抖音": "com.ss.iphone.ugc.Aweme",
    "Douyin": "com.ss.iphone.ugc.Aweme",
    "TikTok": "com.zhiliaoapp.musically",
    "快手": "com.kuaishou.nebula",
    "Kuaishou": "com.kuaishou.nebula",
    "B站": "tv.danmaku.bilianime",
    "哔哩哔哩": "tv.danmaku.bilianime",
    "Bilibili": "tv.danmaku.bilianime",
    "今日头条": "com.ss.iphone.article.News",
    "Toutiao": "com.ss.iphone.article.News",
    "知乎": "com.zhihu.ios",
    "Zhihu": "com.zhihu.ios",
    "豆瓣": "com.douban.frodo",
    "Douban": "com.douban.frodo",
    "网易云音乐": "com.netease.cloudmusic",
    "NetEase Music": "com.netease.cloudmusic",
    "QQ音乐": "com.tencent.QQMusic",
    "QQ Music": "com.tencent.QQMusic",
    "酷狗音乐": "com.kugou.kugou",
    "喜马拉雅": "com.gemd.iting",
    "Ximalaya": "com.gemd.iting",
    "爱奇艺": "com.qiyi.iphone",
    "iQIYI": "com.qiyi.iphone",
    "优酷": "com.youku.YouKu",
    "Youku": "com.youku.YouKu",
    "腾讯视频": "com.tencent.live4iphone",
    "Tencent Video": "com.tencent.live4iphone",
    
    # ===== 工具 Tools =====
    "支付宝": "com.alipay.iphoneclient",
    "Alipay": "com.alipay.iphoneclient",
    "百度": "com.baidu.searchbox",
    "Baidu": "com.baidu.searchbox",
    "夸克": "com.quark.browser",
    "Quark": "com.quark.browser",
    "UC浏览器": "com.ucweb.iphone.lowversion",
    "UC Browser": "com.ucweb.iphone.lowversion",
    "WPS": "cn.wps.moffice_eng",
    "印象笔记": "com.yinxiang.note",
    "Evernote": "com.evernote.iPhone.Evernote",
    "腾讯文档": "com.tencent.docsiphone",
    "石墨文档": "com.shimo.ios",
    
    # ===== 金融 Finance =====
    "招商银行": "cmb.pb",
    "CMB": "cmb.pb",
    "工商银行": "com.icbc.iphoneclient",
    "ICBC": "com.icbc.iphoneclient",
    "建设银行": "com.ccb.iphonepf",
    "CCB": "com.ccb.iphonepf",
    "农业银行": "cn.com.95599.iphone",
    "ABC": "cn.com.95599.iphone",
    "中国银行": "com.boc.bocmbci",
    "BOC": "com.boc.bocmbci",
    
    # ===== 系统应用 System Apps =====
    "Safari": "com.apple.mobilesafari",
    "设置": "com.apple.Preferences",
    "Settings": "com.apple.Preferences",
    "App Store": "com.apple.AppStore",
    "相机": "com.apple.camera",
    "Camera": "com.apple.camera",
    "照片": "com.apple.mobileslideshow",
    "Photos": "com.apple.mobileslideshow",
    "备忘录": "com.apple.mobilenotes",
    "Notes": "com.apple.mobilenotes",
    "日历": "com.apple.mobilecal",
    "Calendar": "com.apple.mobilecal",
    "地图": "com.apple.Maps",
    "Maps": "com.apple.Maps",
    "天气": "com.apple.weather",
    "Weather": "com.apple.weather",
    "时钟": "com.apple.mobiletimer",
    "Clock": "com.apple.mobiletimer",
    "信息": "com.apple.MobileSMS",
    "Messages": "com.apple.MobileSMS",
    "电话": "com.apple.mobilephone",
    "Phone": "com.apple.mobilephone",
    "邮件": "com.apple.mobilemail",
    "Mail": "com.apple.mobilemail",
    "音乐": "com.apple.Music",
    "Music": "com.apple.Music",
    "文件": "com.apple.DocumentsApp",
    "Files": "com.apple.DocumentsApp",
    "健康": "com.apple.Health",
    "Health": "com.apple.Health",
    "钱包": "com.apple.Passbook",
    "Wallet": "com.apple.Passbook",
    "Siri": "com.apple.siri",
    "播客": "com.apple.podcasts",
    "Podcasts": "com.apple.podcasts",
    "图书": "com.apple.iBooks",
    "Books": "com.apple.iBooks",
    "快捷指令": "com.apple.shortcuts",
    "Shortcuts": "com.apple.shortcuts",
    "FaceTime": "com.apple.facetime",
    "查找": "com.apple.findmy",
    "Find My": "com.apple.findmy",
}


def get_bundle_id(app_name: str) -> str | None:
    """
    Get bundle ID for an app name.
    
    Args:
        app_name: App name in Chinese or English
        
    Returns:
        Bundle ID if found, None otherwise
    """
    # Direct match
    if app_name in IOS_APP_PACKAGES:
        return IOS_APP_PACKAGES[app_name]
    
    # Case-insensitive match
    app_lower = app_name.lower()
    for name, bundle_id in IOS_APP_PACKAGES.items():
        if name.lower() == app_lower:
            return bundle_id
    
    return None


def get_app_name(bundle_id: str) -> str | None:
    """
    Get app name for a bundle ID.
    
    Args:
        bundle_id: iOS bundle identifier
        
    Returns:
        App name if found (Chinese preferred), None otherwise
    """
    # Return first matching name (usually Chinese)
    for name, bid in IOS_APP_PACKAGES.items():
        if bid == bundle_id:
            return name
    return None
