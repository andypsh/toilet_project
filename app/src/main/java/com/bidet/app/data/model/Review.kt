package com.bidet.app.data.model

import com.google.firebase.firestore.DocumentId

data class Review(
    @DocumentId val id: String = "",
    val toiletId: String = "",
    val userId: String = "",
    val userName: String = "",
    val rating: Int = 0,
    val cleanliness: Int = 0,
    val bidetWorks: Boolean = true,
    val comment: String = "",
    val photoUrls: List<String> = emptyList(),
    val createdAt: Long = 0L,
)
