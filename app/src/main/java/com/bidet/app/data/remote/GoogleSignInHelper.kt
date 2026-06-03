package com.bidet.app.data.remote

import android.content.Context
import androidx.credentials.CredentialManager
import androidx.credentials.GetCredentialRequest
import com.bidet.app.BuildConfig
import com.google.android.libraries.identity.googleid.GetGoogleIdOption
import com.google.android.libraries.identity.googleid.GoogleIdTokenCredential
import com.google.firebase.auth.GoogleAuthProvider
import com.google.firebase.auth.AuthCredential
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class GoogleSignInHelper @Inject constructor() {

    suspend fun getCredential(context: Context): AuthCredential? {
        if (BuildConfig.GOOGLE_WEB_CLIENT_ID.isBlank()) return null
        val cm = CredentialManager.create(context)
        val opt = GetGoogleIdOption.Builder()
            .setServerClientId(BuildConfig.GOOGLE_WEB_CLIENT_ID)
            .setFilterByAuthorizedAccounts(false)
            .build()
        val req = GetCredentialRequest.Builder().addCredentialOption(opt).build()
        val response = cm.getCredential(context, req)
        val cred = response.credential
        val google = GoogleIdTokenCredential.createFrom(cred.data)
        return GoogleAuthProvider.getCredential(google.idToken, null)
    }
}
