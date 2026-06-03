package com.bidet.app.data.repository

import com.bidet.app.data.model.Report
import com.bidet.app.data.remote.FirestoreSource
import javax.inject.Inject
import javax.inject.Singleton

interface ReportRepository {
    suspend fun submit(report: Report)
}

@Singleton
class ReportRepositoryImpl @Inject constructor(
    private val firestore: FirestoreSource,
) : ReportRepository {
    override suspend fun submit(report: Report) = firestore.submitReport(report)
}
