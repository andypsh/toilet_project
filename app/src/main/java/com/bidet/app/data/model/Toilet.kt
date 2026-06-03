package com.bidet.app.data.model

import com.google.firebase.firestore.DocumentId

data class Toilet(
    @DocumentId val id: String = "",
    val name: String = "",
    val address: String = "",
    val lat: Double = 0.0,
    val lng: Double = 0.0,
    val geohash: String = "",
    val category: ToiletCategory = ToiletCategory.UNKNOWN,
    val hasBidet: Boolean = false,
    val bidetVerified: Boolean = false,
    val bidetCount: Int = 0,
    val gender: GenderAvailability = GenderAvailability.UNKNOWN,
    val accessible: Boolean = false,
    val openHours: String? = null,
    val is24h: Boolean = false,
    val isFree: Boolean = true,
    val rating: Double = 0.0,
    val reviewCount: Int = 0,
    val photoUrls: List<String> = emptyList(),
    val sources: List<DataSource> = emptyList(),
    val createdAt: Long = 0L,
    val updatedAt: Long = 0L,
)

enum class ToiletCategory {
    PUBLIC, DEPARTMENT_STORE, MART, CAFE, RESTAURANT,
    SUBWAY, TRAIN_STATION, AIRPORT, REST_AREA, HOTEL,
    PARK, LIBRARY, GOVERNMENT, UNIVERSITY, HOSPITAL,
    SHOPPING_MALL, GAS_STATION, ETC, UNKNOWN
}

enum class GenderAvailability {
    MEN_ONLY, WOMEN_ONLY, BOTH, UNISEX, UNKNOWN
}

data class DataSource(
    val type: SourceType = SourceType.UNKNOWN,
    val url: String? = null,
    val description: String? = null,
    val collectedAt: Long = 0L,
)

enum class SourceType {
    PUBLIC_DATA,
    OFFICIAL_WEBSITE,
    NEWS,
    BLOG_REVIEW,
    MAP_REVIEW,
    USER_REPORT,
    INFORMATION_DISCLOSURE,
    UNKNOWN
}
