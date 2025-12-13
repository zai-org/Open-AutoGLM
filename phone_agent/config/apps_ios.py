"""App name to iOS bundle ID mapping for supported applications.

Based on iOS app bundle ID conventions and common iOS applications.
Bundle IDs are in the format: com.company.appName
"""

APP_PACKAGES_IOS: dict[str, str] = {
    # Tencent Apps (腾讯系)
    "微信": "com.tencent.xin",
    "企业微信": "com.tencent.ww",
    "微信读书": "com.tencent.weread",
    "微信听书": "com.tencent.wehear",
    "QQ": "com.tencent.mqq",
    "QQ音乐": "com.tencent.QQMusic",
    "QQ阅读": "com.tencent.qqreaderiphone",
    "QQ邮箱": "com.tencent.qqmail",
    "QQ浏览器": "com.tencent.mttlite",
    "TIM": "com.tencent.tim",
    "微视": "com.tencent.microvision",
    "腾讯新闻": "com.tencent.info",
    "腾讯视频": "com.tencent.live4iphone",
    "腾讯动漫": "com.tencent.ied.app.comic",
    "腾讯微云": "com.tencent.weiyun",
    "腾讯体育": "com.tencent.sportskbs",
    "腾讯文档": "com.tencent.txdocs",
    "腾讯翻译君": "com.tencent.qqtranslator",
    "腾讯课堂": "com.tencent.edu",
    "腾讯地图": "com.tencent.sosomap",
    "小鹅拼拼": "com.tencent.dwdcoco",
    "全民k歌": "com.tencent.QQKSong",
    # Alibaba Apps (阿里系)
    "支付宝": "com.alipay.iphoneclient",
    "钉钉": "com.laiwang.DingTalk",
    "闲鱼": "com.taobao.fleamarket",
    "淘宝": "com.taobao.taobao4iphone",
    "斗鱼": "tv.douyu.live",
    "天猫": "com.taobao.tmall",
    "口碑": "com.taobao.kbmeishi",
    "饿了么": "me.ele.ios.eleme",
    "高德地图": "com.autonavi.amap",
    "UC浏览器": "com.ucweb.iphone.lowversion",
    "一淘": "com.taobao.etaocoupon",
    "飞猪": "com.taobao.travel",
    "虾米音乐": "com.xiami.spark",
    "淘票票": "com.taobao.movie.MoviePhoneClient",
    "优酷": "com.youku.YouKu",
    "菜鸟裹裹": "com.cainiao.cnwireless",
    "土豆视频": "com.tudou.tudouiphone",
    # ByteDance Apps (字节系)
    "抖音": "com.ss.iphone.ugc.Aweme",
    "抖音极速版": "com.ss.iphone.ugc.aweme.lite",
    "抖音火山版": "com.ss.iphone.ugc.Live",
    "Tiktok": "com.zhiliaoapp.musically",
    "飞书": "com.bytedance.ee.lark",
    "今日头条": "com.ss.iphone.article.News",
    "西瓜视频": "com.ss.iphone.article.Video",
    "皮皮虾": "com.bd.iphone.super",
    # Meituan Apps (美团系)
    "美团": "com.meituan.imeituan",
    "美团外卖": "com.meituan.itakeaway",
    "大众点评": "com.dianping.dpscope",
    "美团优选": "com.meituan.iyouxuan",
    "美团优选团长": "com.meituan.igrocery.gh",
    "美团骑手": "com.meituan.banma.homebrew",
    "美团开店宝": "com.meituan.imerchantbiz",
    "美团拍店": "com.meituan.pai",
    "美团众包": "com.meituan.banma.crowdsource",
    "美团买菜": "com.baobaoaichi.imaicai",
    # JD Apps (京东系)
    "京东": "com.360buy.jdmobile",
    "京东读书": "com.jd.reader",
    # NetEase Apps (网易系)
    "网易新闻": "com.netease.news",
    "网易云音乐": "com.netease.cloudmusic",
    "网易邮箱大师": "com.netease.macmail",
    "网易严选": "com.netease.yanxuan",
    "网易公开课": "com.netease.videoHD",
    "网易有道词典": "youdaoPro",
    "有道云笔记": "com.youdao.note.YoudaoNoteMac",
    # Baidu Apps (百度系)
    "百度": "com.baidu.BaiduMobile",
    "百度网盘": "com.baidu.netdisk",
    "百度贴吧": "com.baidu.tieba",
    "百度地图": "com.baidu.map",
    "百度阅读": "com.baidu.yuedu",
    "百度翻译": "com.baidu.translate",
    "百度文库": "com.baidu.Wenku",
    "百度视频": "com.baidu.videoiphone",
    "百度输入法": "com.baidu.inputMethod",
    # Kuaishou Apps (快手系)
    "快手": "com.jiangjia.gif",
    "快手极速版": "com.kuaishou.nebula",
    # Other Popular Apps
    "哔哩哔哩": "tv.danmaku.bilianime",
    "芒果TV": "com.hunantv.imgotv",
    "苏宁易购": "SuningEMall",
    "微博": "com.sina.weibo",
    "微博极速版": "com.sina.weibolite",
    "微博国际": "com.weibo.international",
    "墨客": "com.moke.moke.iphone",
    "豆瓣": "com.douban.frodo",
    "知乎": "com.zhihu.ios",
    "小红书": "com.xingin.discover",
    "喜马拉雅": "com.gemd.iting",
    "得到": "com.luojilab.LuoJiFM-IOS",
    "得物": "com.siwuai.duapp",
    "起点读书": "m.qidian.QDReaderAppStore",
    "番茄小说": "com.dragon.read",
    "书旗小说": "com.shuqicenter.reader",
    "拼多多": "com.xunmeng.pinduoduo",
    "多点": "com.dmall.dmall",
    "便利蜂": "com.bianlifeng.customer.ios",
    "亿通行": "com.ruubypay.yitongxing",
    "云闪付": "com.unionpay.chsp",
    "大都会Metro": "com.DDH.SHSubway",
    "爱奇艺视频": "com.qiyi.iphone",
    "搜狐视频": "com.sohu.iPhoneVideo",
    "搜狐新闻": "com.sohu.newspaper",
    "搜狗浏览器": "com.sogou.SogouExplorerMobile",
    "虎牙": "com.yy.kiwi",
    "比心": "com.yitan.bixin",
    "转转": "com.wuba.zhuanzhuan",
    "YY": "yyvoice",
    "绿洲": "com.sina.oasis",
    "陌陌": "com.wemomo.momoappdemo1",
    "什么值得买": "com.smzdm.client.ios",
    "美团秀秀": "com.meitu.mtxx",
    "唯品会": "com.vipshop.iphone",
    "唱吧": "com.changba.ktv",
    "酷狗音乐": "com.kugou.kugou1002",
    "CSDN": "net.csdn.CsdnPlus",
    "多抓鱼": "com.duozhuyu.dejavu",
    "自如": "com.ziroom.ZiroomProject",
    "携程": "ctrip.com",
    "去哪儿旅行": "com.qunar.iphoneclient8",
    "Xmind": "net.xmind.brownieapp",
    "印象笔记": "com.yinxiang.iPhone",
    "欧陆词典": "eusoft.eudic.pro",
    "115": "com.115.personal",
    "名片全能王": "com.intsig.camcard.lite",
    "中国银行": "com.boc.BOCMBCI",
    "58同城": "com.taofang.iphone",
    # International Apps
    "Google Chrome": "com.google.chrome.ios",
    "Gmail": "com.google.Gmail",
    "Facebook": "com.facebook.Facebook",
    "Firefox": "org.mozilla.ios.Firefox",
    "Messenger": "com.facebook.Messenger",
    "Instagram": "com.burbn.instagram",
    "Starbucks": "com.starbucks.mystarbucks",
    "Luckin Coffee": "com.bjlc.luckycoffee",
    "Line": "jp.naver.line",
    "Linkedin": "com.linkedin.LinkedIn",
    "Dcard": "com.dcard.app.Dcard",
    "Youtube": "com.google.ios.youtube",
    "Spotify": "com.spotify.client",
    "Netflix": "com.netflix.Netflix",
    "Twitter": "com.atebits.Tweetie2",
    "WhatsApp": "net.whatsapp.WhatsApp",
    # Apple Native Apps (Apple 原生应用)
    "Safari": "com.apple.mobilesafari",
    "App Store": "com.apple.AppStore",
    "设置": "com.apple.Preferences",
    "相机": "com.apple.camera",
    "照片": "com.apple.mobileslideshow",
    "时钟": "com.apple.mobiletimer",
    "闹钟": "com.apple.mobiletimer",
    "备忘录": "com.apple.mobilenotes",
    "提醒事项": "com.apple.reminders",
    "快捷指令": "com.apple.shortcuts",
    "天气": "com.apple.weather",
    "日历": "com.apple.mobilecal",
    "地图": "com.apple.Maps",
    "电话": "com.apple.mobilephone",
    "通讯录": "com.apple.MobileAddressBook",
    "信息": "com.apple.MobileSMS",
    "Facetime": "com.apple.facetime",
    "FaceTime": "com.apple.facetime",
    "计算器": "com.apple.calculator",
    "家庭": "com.apple.Home",
    "健康": "com.apple.Health",
    "钱包": "com.apple.Passbook",
    "股市": "com.apple.stocks",
    "图书": "com.apple.iBooks",
    "新闻": "com.apple.news",
    "视频": "com.apple.tv",
    "文件": "com.apple.DocumentsApp",
    "邮件": "com.apple.mobilemail",
    "查找": "com.apple.findmy",
    "翻译": "com.apple.Translate",
    "音乐": "com.apple.Music",
    "播客": "com.apple.podcasts",
    "库乐队": "com.apple.mobilegarageband",
    "语音备忘录": "com.apple.VoiceMemos",
    "iMovie": "com.apple.iMovie",
    "Watch": "com.apple.Bridge",
    "Apple Store": "com.apple.store.Jolly",
    "TestFlight": "com.apple.TestFlight",
    "Keynote": "com.apple.Keynote",
    "Keynote 讲演": "com.apple.Keynote",
}


def get_bundle_id(app_name: str) -> str | None:
    """
    Get the iOS bundle ID for an app.

    Args:
        app_name: The display name of the app.

    Returns:
        The iOS bundle ID, or None if not found.
    """
    return APP_PACKAGES_IOS.get(app_name)


def get_app_name(bundle_id: str) -> str | None:
    """
    Get the app name from an iOS bundle ID.

    Args:
        bundle_id: The iOS bundle ID.

    Returns:
        The display name of the app, or None if not found.
    """
    for name, bid in APP_PACKAGES_IOS.items():
        if bid == bundle_id:
            return name
    return None


def list_supported_apps() -> list[str]:
    """
    Get a list of all supported iOS app names.

    Returns:
        List of app names.
    """
    return list(APP_PACKAGES_IOS.keys())


def check_app_installed(app_name: str, wda_url: str = "http://localhost:8100") -> bool:
    """
    Check if an app is installed on the iOS device.

    Args:
        app_name: The display name of the app.
        wda_url: WebDriverAgent URL.

    Returns:
        True if app is installed, False otherwise.

    Note:
        This uses the iTunes API to get app information. For actual
        installation check on device, you would need to use WDA's
        app listing capabilities or URL scheme checking.
    """
    bundle_id = get_bundle_id(app_name)
    if not bundle_id:
        return False

    try:
        import requests

        # Query iTunes API for app info
        url = f"https://itunes.apple.com/lookup?bundleId={bundle_id}"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            return data.get("resultCount", 0) > 0

    except ImportError:
        print("Error: requests library required. Install: pip install requests")
    except Exception as e:
        print(f"Error checking app installation: {e}")

    return False


def get_app_info_from_itunes(bundle_id: str) -> dict | None:
    """
    Get app information from iTunes API using bundle ID.

    Args:
        bundle_id: The iOS bundle ID.

    Returns:
        Dictionary with app info (name, version, etc.) or None if not found.
    """
    try:
        import requests

        url = f"https://itunes.apple.com/lookup?bundleId={bundle_id}"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            if results:
                return results[0]

    except ImportError:
        print("Error: requests library required. Install: pip install requests")
    except Exception as e:
        print(f"Error fetching app info: {e}")

    return None


def get_app_info_by_id(app_store_id: str) -> dict | None:
    """
    Get app information from iTunes API using App Store ID.

    Args:
        app_store_id: The numeric App Store ID (e.g., "414478124" for WeChat).

    Returns:
        Dictionary with app info or None if not found.
    """
    try:
        import requests

        url = f"https://itunes.apple.com/lookup?id={app_store_id}"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            if results:
                return results[0]

    except ImportError:
        print("Error: requests library required. Install: pip install requests")
    except Exception as e:
        print(f"Error fetching app info by ID: {e}")

    return None
