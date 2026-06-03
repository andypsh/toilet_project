package com.bidet.app.data.repository

import com.bidet.app.data.model.User
import com.bidet.app.data.remote.FirebaseAuthSource
import com.bidet.app.data.remote.FirestoreSource
import com.google.firebase.auth.AuthCredential
import com.google.firebase.auth.FirebaseUser
import kotlinx.coroutines.flow.Flow
import javax.inject.Inject
import javax.inject.Singleton

interface AuthRepository {
    fun currentUser(): FirebaseUser?
    fun authStateFlow(): Flow<FirebaseUser?>
    suspend fun signIn(credential: AuthCredential): User?
    fun signOut()
}

@Singleton
class AuthRepositoryImpl @Inject constructor(
    private val authSource: FirebaseAuthSource,
    private val firestore: FirestoreSource,
) : AuthRepository {

    override fun currentUser(): FirebaseUser? = authSource.currentUser()
    override fun authStateFlow(): Flow<FirebaseUser?> = authSource.authStateFlow()

    override suspend fun signIn(credential: AuthCredential): User? {
        val fbUser = authSource.signInWithCredential(credential) ?: return null
        val existing = firestore.getUser(fbUser.uid)
        return existing ?: User(
            uid = fbUser.uid,
            nickname = fbUser.displayName ?: "익명",
            email = fbUser.email,
            photoUrl = fbUser.photoUrl?.toString(),
            provider = fbUser.providerId,
            createdAt = System.currentTimeMillis(),
        ).also { firestore.upsertUser(it) }
    }

    override fun signOut() = authSource.signOut()
}
