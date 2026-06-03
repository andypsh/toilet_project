package com.bidet.app.domain.usecase

import com.bidet.app.data.model.Report
import com.bidet.app.data.repository.ReportRepository
import javax.inject.Inject

class SubmitReportUseCase @Inject constructor(
    private val repo: ReportRepository
) {
    suspend operator fun invoke(report: Report) = repo.submit(
        report.copy(createdAt = System.currentTimeMillis())
    )
}
