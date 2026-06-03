package com.bidet.app.domain.usecase

import com.bidet.app.data.model.Toilet
import com.bidet.app.data.repository.ToiletRepository
import javax.inject.Inject

class GetNearbyToiletsUseCase @Inject constructor(
    private val repo: ToiletRepository
) {
    suspend operator fun invoke(lat: Double, lng: Double, radiusKm: Double = 2.0): List<Toilet> =
        repo.getNearby(lat, lng, radiusKm)
}
