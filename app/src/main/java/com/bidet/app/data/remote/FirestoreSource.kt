package com.bidet.app.data.remote

import com.bidet.app.data.model.Report
import com.bidet.app.data.model.Review
import com.bidet.app.data.model.Toilet
import com.bidet.app.data.model.User
import com.google.firebase.firestore.FirebaseFirestore
import kotlinx.coroutines.tasks.await
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class FirestoreSource @Inject constructor(
    private val db: FirebaseFirestore
) {
    suspend fun getToilet(id: String): Toilet? =
        db.collection(COL_TOILETS).document(id).get().await()
            .toObject(Toilet::class.java)

    suspend fun getToiletsByGeohashRange(start: String, end: String, limit: Long = 200): List<Toilet> =
        db.collection(COL_TOILETS)
            .whereEqualTo("hasBidet", true)
            .orderBy("geohash")
            .startAt(start)
            .endAt(end)
            .limit(limit)
            .get().await()
            .toObjects(Toilet::class.java)

    suspend fun searchToiletsByName(keyword: String, limit: Long = 30): List<Toilet> =
        db.collection(COL_TOILETS)
            .whereEqualTo("hasBidet", true)
            .orderBy("name")
            .startAt(keyword)
            .endAt(keyword + "")
            .limit(limit)
            .get().await()
            .toObjects(Toilet::class.java)

    suspend fun getReviewsForToilet(toiletId: String, limit: Long = 50): List<Review> =
        db.collection(COL_REVIEWS)
            .whereEqualTo("toiletId", toiletId)
            .orderBy("createdAt")
            .limit(limit)
            .get().await()
            .toObjects(Review::class.java)

    suspend fun addReview(review: Review) {
        db.collection(COL_REVIEWS).add(review).await()
    }

    suspend fun submitReport(report: Report) {
        db.collection(COL_REPORTS).add(report).await()
    }

    suspend fun getUser(uid: String): User? =
        db.collection(COL_USERS).document(uid).get().await()
            .toObject(User::class.java)

    suspend fun upsertUser(user: User) {
        db.collection(COL_USERS).document(user.uid).set(user).await()
    }

    suspend fun toggleFavorite(uid: String, toiletId: String): Boolean {
        val ref = db.collection(COL_USERS).document(uid)
        val user = ref.get().await().toObject(User::class.java) ?: return false
        val current = user.favoriteToiletIds
        val updated = if (current.contains(toiletId)) current - toiletId else current + toiletId
        ref.update("favoriteToiletIds", updated).await()
        return updated.contains(toiletId)
    }

    companion object {
        const val COL_TOILETS = "toilets"
        const val COL_REVIEWS = "reviews"
        const val COL_USERS = "users"
        const val COL_REPORTS = "reports"
    }
}
