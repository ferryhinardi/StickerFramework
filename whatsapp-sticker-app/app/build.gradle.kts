plugins {
    id("com.android.application")
}

val appId = "com.bobastickers.whatsapp"

android {
    namespace = appId
    compileSdk = 34

    defaultConfig {
        applicationId = appId
        minSdk = 21
        targetSdk = 34
        versionCode = 1
        versionName = "1.0.0"

        // ContentProvider authority — must match AndroidManifest
        buildConfigField("String", "CONTENT_PROVIDER_AUTHORITY",
            "\"${appId}.stickercontentprovider\"")

        // Server URL for dynamic pack loading (override via local.properties or CI)
        buildConfigField("String", "STICKER_API_BASE_URL",
            "\"http://10.0.2.2:8080\"")  // Android emulator → host localhost
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
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    buildFeatures {
        buildConfig = true
    }
}

dependencies {
    // AndroidX
    implementation("androidx.appcompat:appcompat:1.6.1")
    implementation("androidx.recyclerview:recyclerview:1.3.2")
    implementation("com.google.android.material:material:1.11.0")
    implementation("androidx.constraintlayout:constraintlayout:2.1.4")

    // Networking (for dynamic pack loading from server)
    implementation("com.squareup.okhttp3:okhttp:4.12.0")

    // JSON parsing
    implementation("com.google.code.gson:gson:2.10.1")

    // Image loading
    implementation("com.github.bumptech.glide:glide:4.16.0")
    annotationProcessor("com.github.bumptech.glide:compiler:4.16.0")
}
