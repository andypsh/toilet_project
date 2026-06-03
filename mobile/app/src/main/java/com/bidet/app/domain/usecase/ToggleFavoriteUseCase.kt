package com.bidet.app.domain.usecase

import com.bidet.app.data.repository.AuthRepository
import com.bidet.app.data.repository.ToiletRepository
import javax.inject.Inject

class ToggleFavoriteUseCase @Inject constructor(
    private val toiletRepo: ToiletRepository,
    private val authRepo: AuthRepository,
) {
    suspend operator fun invoke(toiletId: String): Boolean {
        val uid = authRepo.currentUser()?.uid ?: return false
        return toiletRepo.toggleFavorite(uid, toiletId)
    }
}
