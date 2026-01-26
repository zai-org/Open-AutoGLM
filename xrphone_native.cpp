#include "xrphone_native.hpp"
#include <jni.h>

extern "C" JNIEXPORT jboolean JNICALL
Java_com_infra_xrphone_XrPhone_initOpenXrAndVulkanNative(
    JNIEnv* env,
    jobject thiz,
    jobject context
) {
    return xrphone_init_openxr_vulkan(env, context) ? JNI_TRUE : JNI_FALSE;
}

extern "C" JNIEXPORT void JNICALL
Java_com_infra_xrphone_XrPhone_resumeOpenXrNative(
    JNIEnv* env, jobject thiz
) {
    xrphone_resume();
}

extern "C" JNIEXPORT void JNICALL
Java_com_infra_xrphone_XrPhone_pauseOpenXrNative(
    JNIEnv* env, jobject thiz
) {
    xrphone_pause();
}

extern "C" JNIEXPORT void JNICALL
Java_com_infra_xrphone_XrPhone_shutdownOpenXrNative(
    JNIEnv* env, jobject thiz
) {
    xrphone_shutdown();
}

extern "C" JNIEXPORT jobject JNICALL
Java_com_infra_xrphone_XrPhone_getHeadPoseNative(
    JNIEnv* env, jobject thiz
) {
    HeadPoseNative pose = xrphone_get_head_pose();
    jclass poseCls = env->FindClass("com/infra/xrphone/XrPhone$HeadPose");
    jmethodID ctor = env->GetMethodID(
        poseCls,
        "<init>",
        "(JFFFFFFF)V"
    );
    return env->NewObject(
        poseCls,
        ctor,
        (jlong)pose.timestampNs,
        pose.px, pose.py, pose.pz,
        pose.qx, pose.qy, pose.qz, pose.qw
    );
}
