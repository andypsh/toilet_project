package com.bidet.app

import android.app.Application
import android.util.Log
import com.kakao.sdk.common.KakaoSdk
import dagger.hilt.android.HiltAndroidApp

@HiltAndroidApp
class BidetApplication : Application() {
    override fun onCreate() {
        super.onCreate()
        if (BuildConfig.DEMO_MODE) {
            Log.i("BidetApp", "Running in DEMO mode — Firebase/Kakao 미초기화, fake 데이터 사용")
        }
        if (BuildConfig.KAKAO_NATIVE_APP_KEY.isNotBlank()) {
            runCatching { KakaoSdk.init(this, BuildConfig.KAKAO_NATIVE_APP_KEY) }
                .onFailure { Log.w("BidetApp", "KakaoSdk init 실패", it) }
        }
    }
}
