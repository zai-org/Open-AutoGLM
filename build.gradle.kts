// File: xrphone/build.gradle.kts
plugins {
    alias(libs.plugins.android.library)
    alias(libs.plugins.kotlin.android)
}

android {
    namespace = "com.infra.xrphone"
    compileSdk = 35

    defaultConfig {
        minSdk = 30
        targetSdk = 35

        externalNativeBuild {
            cmake {
                cppFlags += "-std=c++17"
            }
        }

        ndk {
            abiFilters += listOf("arm64-v8a")
        }

        consumerProguardFiles("consumer-rules.pro")
    }

    buildTypes {
        release {
            isMinifyEnabled = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
        debug {
            isMinifyEnabled = false
            matchingFallbacks += listOf("release")
        }
    }

    externalNativeBuild {
        cmake {
            path = file("src/main/cpp/CMakeLists.txt")
        }
    }

    buildFeatures {
        compose = true
    }

    composeOptions {
        kotlinCompilerExtensionVersion = "1.7.0"
    }

    packaging {
        resources {
            excludes += listOf("META-INF/LICENSE*", "META-INF/NOTICE*")
        }
    }
}

dependencies {
    // === Core Kotlin/Android ===
    implementation(libs.androidx.core.ktx)
    implementation(libs.kotlin.stdlib)
    implementation(libs.coroutines.android)

    // === Jetpack XR / Compose XR (Android XR SDK integration) ===
    implementation(libs.xr.core)
    implementation(libs.xr.compose)

    // === Network / InfraNet stack ===
    implementation(libs.java.websocket)
    implementation(libs.okhttp)

    // === Serialization & Data Layer ===
    implementation(libs.serialization.json)
}
