plugins {
    kotlin("jvm") version "2.1.20"
    id("org.jetbrains.compose")
}

dependencies {
    implementation(compose.desktop.currentOs)
}

compose.desktop {
    application {
        mainClass = "com.strangerdanger.desktop.MainKt"
    }
}
