package com.bidet.app.data.repository

import com.bidet.app.data.model.Review
import com.bidet.app.data.model.Toilet
import com.bidet.app.data.remote.FirestoreSource
import com.bidet.app.util.Geohash
import javax.inject.Inject
import javax.inject.Singleton

interface ToiletRepository {
    suspend fun getNearby(lat: Double, lng: Double, radiusKm: Double): List<Toilet>
    suspend fun get(id: String): Toilet?
    suspend fun searchByName(keyword: String): List<Toilet>
    suspend fun getReviews(toiletId: String): List<Review>
    suspend fun addReview(review: Review)
    suspend fun toggleFavorite(uid: String, toiletId: String): Boolean
    suspend fun isFavorite(uid: String, toiletId: String): Boolean
}

@Singleton
class ToiletRepositoryImpl @Inject constructor(
    private val firestore: FirestoreSource,
) : ToiletRepository {

    override suspend fun getNearby(lat: Double, lng: Double, radiusKm: Double): List<Toilet> {
        val (start, end) = Geohash.boundsForRadius(lat, lng, radiusKm)
        val results = firestore.getToiletsByGeohashRange(start, end)
        return results.filter {
            Geohash.distanceKm(lat, lng, it.lat, it.lng) <= radiusKm
        }
    }

    override suspend fun get(id: String): Toilet? = firestore.getToilet(id)

    override suspend fun searchByName(keyword: String): List<Toilet> =
        firestore.searchToiletsByName(keyword)

    override suspend fun getReviews(toiletId: String): List<Review> =
        firestore.getReviewsForToilet(toiletId)

    override suspend fun addReview(review: Review) = firestore.addReview(review)

    override suspend fun toggleFavorite(uid: String, toiletId: String): Boolean =
        firestore.toggleFavorite(uid, toiletId)

    override suspend fun isFavorite(uid: String, toiletId: String): Boolean =
        firestore.getUser(uid)?.favoriteToiletIds?.contains(toiletId) ?: false
}
