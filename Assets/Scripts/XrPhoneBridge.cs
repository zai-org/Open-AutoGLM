using UnityEngine;

public class XrPhoneBridge : MonoBehaviour
{
    AndroidJavaObject xrPhone;

    void Start()
    {
        if (Application.platform != RuntimePlatform.Android)
            return;

        using var unityPlayer = new AndroidJavaClass("com.unity3d.player.UnityPlayer");
        var activity = unityPlayer.GetStatic<AndroidJavaObject>("currentActivity");

        var context = activity.Call<AndroidJavaObject>("getApplicationContext");
        var lifecycleOwner = activity; // if activity implements LifecycleOwner via AndroidX
        xrPhone = new AndroidJavaObject(
            "com.infra.xrphone.XrPhone",
            context,
            "wss://infranet.example.com/xr",
            SystemInfo.deviceUniqueIdentifier,
            lifecycleOwner
        );

        xrPhone.Call("attachUnitySession", activity);
    }

    void OnDestroy()
    {
        xrPhone?.Call("shutdown");
    }
}
