package com.bidet.app.domain.usecase

import com.bidet.app.data.model.Toilet
import com.bidet.app.data.repository.ToiletRepository
import javax.inject.Inject

class SearchToiletsUseCase @Inject constructor(
    private val repo: ToiletRepository
) {
    suspend operator fun invoke(keyword: String): List<Toilet> {
        if (keyword.isBlank()) return emptyList()
        return repo.searchByName(keyword.trim())
    }
}
