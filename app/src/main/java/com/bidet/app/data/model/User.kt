package com.bidet.app.data.model

import com.google.firebase.firestore.DocumentId

data class User(
    @DocumentId val uid: String = "",
    val nickname: String = "",
    val email: String? = null,
    val photoUrl: String? = null,
    val provider: String = "",
    val reportCount: Int = 0,
    val reviewCount: Int = 0,
    val favoriteToiletIds: List<String> = emptyList(),
    val createdAt: Long = 0L,
)
