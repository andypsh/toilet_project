package com.bidet.app.data.demo

import com.bidet.app.data.model.Report
import com.bidet.app.data.model.Review
import com.bidet.app.data.model.Toilet
import com.bidet.app.data.repository.AuthRepository
import com.bidet.app.data.repository.ReportRepository
import com.bidet.app.data.repository.ToiletRepository
import com.bidet.app.util.Geohash
import com.google.firebase.auth.AuthCredential
import com.google.firebase.auth.FirebaseUser
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flowOf
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class FakeToiletRepository @Inject constructor() : ToiletRepository {

    private val toilets = DemoData.toilets.toMutableList()
    private val reviews = DemoData.reviews.toMutableMap()
    private val favorites = mutableSetOf<String>()

    override suspend fun getNearby(lat: Double, lng: Double, radiusKm: Double): List<Toilet> {
        return toilets.filter {
            Geohash.distanceKm(lat, lng, it.lat, it.lng) <= radiusKm
        }
    }

    override suspend fun get(id: String): Toilet? = toilets.find { it.id == id }

    override suspend fun searchByName(keyword: String): List<Toilet> =
        toilets.filter { it.name.contains(keyword, ignoreCase = true) }

    override suspend fun getReviews(toiletId: String): List<Review> =
        reviews[toiletId] ?: emptyList()

    override suspend fun addReview(review: Review) {
        val list = reviews.getOrPut(review.toiletId) { mutableListOf() }.toMutableList()
        list.add(review.copy(id = "r-${System.currentTimeMillis()}"))
        reviews[review.toiletId] = list
    }

    override suspend fun toggleFavorite(uid: String, toiletId: String): Boolean {
        return if (favorites.contains(toiletId)) {
            favorites.remove(toiletId); false
        } else {
            favorites.add(toiletId); true
        }
    }

    override suspend fun isFavorite(uid: String, toiletId: String): Boolean =
        favorites.contains(toiletId)
}

@Singleton
class FakeAuthRepository @Inject constructor() : AuthRepository {
    override fun currentUser(): FirebaseUser? = null
    override fun authStateFlow(): Flow<FirebaseUser?> = flowOf(null)
    override suspend fun signIn(credential: AuthCredential) = null
    override fun signOut() {}
}

@Singleton
class FakeReportRepository @Inject constructor() : ReportRepository {
    private val submitted = mutableListOf<Report>()
    override suspend fun submit(report: Report) {
        submitted.add(report.copy(id = "report-${System.currentTimeMillis()}"))
    }
}
