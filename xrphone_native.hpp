#pragma once
#include <jni.h>

struct HeadPoseNative {
    long timestampNs;
    float px, py, pz;
    float qx, qy, qz, qw;
};

bool xrphone_init_openxr_vulkan(JNIEnv* env, jobject context);
void xrphone_resume();
void xrphone_pause();
void xrphone_shutdown();
HeadPoseNative xrphone_get_head_pose();
