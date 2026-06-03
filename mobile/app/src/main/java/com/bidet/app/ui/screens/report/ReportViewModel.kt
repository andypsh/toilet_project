package com.bidet.app.ui.screens.report

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.bidet.app.data.model.Report
import com.bidet.app.data.model.ReportType
import com.bidet.app.domain.usecase.SubmitReportUseCase
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

data class ReportUiState(
    val name: String = "",
    val address: String = "",
    val hasBidet: Boolean = true,
    val description: String = "",
    val submitting: Boolean = false,
    val submitted: Boolean = false,
)

@HiltViewModel
class ReportViewModel @Inject constructor(
    private val submitReport: SubmitReportUseCase,
) : ViewModel() {

    private val _state = MutableStateFlow(ReportUiState())
    val state: StateFlow<ReportUiState> = _state.asStateFlow()

    fun onName(v: String) { _state.value = _state.value.copy(name = v) }
    fun onAddress(v: String) { _state.value = _state.value.copy(address = v) }
    fun onHasBidet(v: Boolean) { _state.value = _state.value.copy(hasBidet = v) }
    fun onDescription(v: String) { _state.value = _state.value.copy(description = v) }

    fun submit(userId: String) {
        val s = _state.value
        _state.value = s.copy(submitting = true)
        viewModelScope.launch {
            runCatching {
                submitReport(
                    Report(
                        userId = userId,
                        type = ReportType.NEW_TOILET,
                        name = s.name,
                        address = s.address,
                        hasBidet = s.hasBidet,
                        description = s.description,
                    )
                )
            }
            _state.value = s.copy(submitting = false, submitted = true)
        }
    }
}
