plugins {
    id("com.android.application")
    kotlin("android") version "2.1.20"
}

android {
    namespace = "com.strangerdanger.android"
    compileSdk = 35

    defaultConfig {
        applicationId = "com.strangerdanger.android"
        minSdk = 26
        targetSdk = 35
        versionCode = 1
        versionName = "1.0.0"
    }

    buildTypes {
        release {
            isMinifyEnabled = false
        }
    }
}
