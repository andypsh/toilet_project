package com.bidet.app.data.model

import com.google.firebase.firestore.DocumentId

data class Report(
    @DocumentId val id: String = "",
    val toiletId: String? = null,
    val userId: String = "",
    val type: ReportType = ReportType.NEW_TOILET,
    val name: String = "",
    val address: String = "",
    val lat: Double = 0.0,
    val lng: Double = 0.0,
    val hasBidet: Boolean = false,
    val description: String = "",
    val photoUrls: List<String> = emptyList(),
    val status: ReportStatus = ReportStatus.PENDING,
    val createdAt: Long = 0L,
)

enum class ReportType {
    NEW_TOILET,
    BIDET_STATUS_UPDATE,
    INCORRECT_INFO,
    PERMANENTLY_CLOSED
}

enum class ReportStatus {
    PENDING, APPROVED, REJECTED, MERGED
}
