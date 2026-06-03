package com.bidet.app.domain.usecase

import com.bidet.app.data.model.Review
import com.bidet.app.data.repository.AuthRepository
import com.bidet.app.data.repository.ToiletRepository
import javax.inject.Inject

class AddReviewUseCase @Inject constructor(
    private val toiletRepo: ToiletRepository,
    private val authRepo: AuthRepository,
) {
    suspend operator fun invoke(
        toiletId: String,
        rating: Int,
        cleanliness: Int,
        bidetWorks: Boolean,
        comment: String,
        photoUrls: List<String> = emptyList(),
    ) {
        val user = authRepo.currentUser() ?: error("로그인 필요")
        toiletRepo.addReview(
            Review(
                toiletId = toiletId,
                userId = user.uid,
                userName = user.displayName ?: "익명",
                rating = rating,
                cleanliness = cleanliness,
                bidetWorks = bidetWorks,
                comment = comment,
                photoUrls = photoUrls,
                createdAt = System.currentTimeMillis(),
            )
        )
    }
}
