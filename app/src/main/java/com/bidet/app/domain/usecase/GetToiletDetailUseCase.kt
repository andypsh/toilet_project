package com.bidet.app.domain.usecase

import com.bidet.app.data.model.Review
import com.bidet.app.data.model.Toilet
import com.bidet.app.data.repository.ToiletRepository
import javax.inject.Inject

data class ToiletDetail(val toilet: Toilet, val reviews: List<Review>)

class GetToiletDetailUseCase @Inject constructor(
    private val repo: ToiletRepository
) {
    suspend operator fun invoke(id: String): ToiletDetail? {
        val t = repo.get(id) ?: return null
        val reviews = repo.getReviews(id)
        return ToiletDetail(t, reviews)
    }
}
