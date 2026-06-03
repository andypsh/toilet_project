package com.bidet.app.ui.screens.auth

import android.content.Context
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.bidet.app.data.remote.GoogleSignInHelper
import com.bidet.app.data.remote.KakaoSignInHelper
import com.bidet.app.data.repository.AuthRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

data class AuthUiState(
    val loading: Boolean = false,
    val error: String? = null,
    val signedIn: Boolean = false,
)

@HiltViewModel
class AuthViewModel @Inject constructor(
    private val authRepository: AuthRepository,
    private val googleHelper: GoogleSignInHelper,
    private val kakaoHelper: KakaoSignInHelper,
) : ViewModel() {

    private val _state = MutableStateFlow(AuthUiState(signedIn = authRepository.currentUser() != null))
    val state: StateFlow<AuthUiState> = _state.asStateFlow()

    fun signInWithGoogle(context: Context) {
        _state.value = _state.value.copy(loading = true, error = null)
        viewModelScope.launch {
            runCatching {
                val cred = googleHelper.getCredential(context)
                    ?: error("Google Web Client ID 미설정")
                authRepository.signIn(cred)
            }.onSuccess {
                _state.value = AuthUiState(signedIn = it != null)
            }.onFailure {
                _state.value = AuthUiState(error = it.message)
            }
        }
    }

    fun signInWithKakao(context: Context) {
        _state.value = _state.value.copy(loading = true, error = null)
        viewModelScope.launch {
            runCatching {
                val token = kakaoHelper.loginAndGetToken(context)
                    ?: error("카카오 로그인 실패")
                // TODO: token.accessToken을 Firebase Cloud Function으로 보내서
                //       Custom Token 받아오는 API 호출 필요.
                //       서버 구현 전까지는 메시지로 안내.
                error("카카오 로그인은 Firebase Custom Token 서버 함수 구현 필요 — Google 로그인 사용")
            }.onFailure {
                _state.value = AuthUiState(error = it.message)
            }
        }
    }

    fun signOut() {
        authRepository.signOut()
        _state.value = AuthUiState(signedIn = false)
    }
}
