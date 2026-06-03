package com.bidet.app.data.remote

import android.content.Context
import com.kakao.sdk.auth.model.OAuthToken
import com.kakao.sdk.common.KakaoSdk
import com.kakao.sdk.user.UserApiClient
import kotlinx.coroutines.suspendCancellableCoroutine
import javax.inject.Inject
import javax.inject.Singleton
import kotlin.coroutines.resume

@Singleton
class KakaoSignInHelper @Inject constructor() {

    fun init(context: Context, appKey: String) {
        if (appKey.isNotBlank()) KakaoSdk.init(context, appKey)
    }

    /**
     * 카카오 OAuth로 토큰을 받음.
     * 이후 이 access_token을 Cloud Function으로 보내 Firebase Custom Token 발급받아야 함.
     * (Firebase는 카카오 OIDC를 직접 지원하지 않아서 한 단계 더 필요)
     */
    suspend fun loginAndGetToken(context: Context): OAuthToken? = suspendCancellableCoroutine { cont ->
        val client = UserApiClient.instance
        val callback: (OAuthToken?, Throwable?) -> Unit = { token, error ->
            if (cont.isActive) {
                if (error != null) cont.resume(null)
                else cont.resume(token)
            }
        }
        if (client.isKakaoTalkLoginAvailable(context)) {
            client.loginWithKakaoTalk(context) { token, error ->
                if (error != null) {
                    client.loginWithKakaoAccount(context, callback = callback)
                } else callback(token, null)
            }
        } else {
            client.loginWithKakaoAccount(context, callback = callback)
        }
    }
}
