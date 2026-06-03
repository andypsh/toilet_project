# 카카오 SDK
-keep class com.kakao.** { *; }
-keep class com.kakao.sdk.**.model.* { *; }
-keep class * extends com.google.gson.TypeAdapter

# Firebase / Firestore — 모델 클래스의 reflection 사용
-keep class com.bidet.app.data.model.** { *; }
-keepattributes Signature
-keepattributes *Annotation*
-keepclassmembers class com.bidet.app.data.model.** {
    <init>(...);
    <fields>;
}

# Moshi (Kotlin reflection)
-keepclasseswithmembers class * {
    @com.squareup.moshi.* <methods>;
}
-keep @com.squareup.moshi.JsonQualifier interface *
-keepclassmembers class kotlin.Metadata {
    public <methods>;
}

# OkHttp / Retrofit
-dontwarn okhttp3.**
-dontwarn okio.**
-dontwarn retrofit2.**
-keepattributes Exceptions

# Hilt
-keep class dagger.hilt.** { *; }
-keep class * extends dagger.hilt.android.internal.lifecycle.HiltViewModelFactory$ViewModelComponent { *; }

# Coroutines
-keepnames class kotlinx.coroutines.internal.MainDispatcherFactory {}
-keepnames class kotlinx.coroutines.CoroutineExceptionHandler {}
