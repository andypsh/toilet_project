package com.bidet.app.ui.screens.detail

import android.net.Uri
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.bidet.app.data.repository.AuthRepository
import com.bidet.app.data.repository.ToiletRepository
import com.bidet.app.domain.usecase.AddReviewUseCase
import com.bidet.app.domain.usecase.GetToiletDetailUseCase
import com.bidet.app.domain.usecase.ToggleFavoriteUseCase
import com.bidet.app.domain.usecase.ToiletDetail
import com.bidet.app.domain.usecase.UploadPhotoUseCase
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

data class DetailUiState(
    val loading: Boolean = false,
    val detail: ToiletDetail? = null,
    val isFavorite: Boolean = false,
    val error: String? = null,
    val submittingReview: Boolean = false,
)

@HiltViewModel
class ToiletDetailViewModel @Inject constructor(
    private val getDetail: GetToiletDetailUseCase,
    private val toggleFav: ToggleFavoriteUseCase,
    private val addReview: AddReviewUseCase,
    private val uploadPhoto: UploadPhotoUseCase,
    private val authRepository: AuthRepository,
    private val toiletRepo: ToiletRepository,
) : ViewModel() {

    private val _state = MutableStateFlow(DetailUiState())
    val state: StateFlow<DetailUiState> = _state.asStateFlow()

    private var toiletId: String = ""

    fun load(id: String) {
        toiletId = id
        _state.value = DetailUiState(loading = true)
        viewModelScope.launch {
            runCatching {
                val d = getDetail(id)
                val uid = authRepository.currentUser()?.uid
                val fav = uid?.let { toiletRepo.isFavorite(it, id) } ?: false
                d to fav
            }.onSuccess { (d, fav) ->
                _state.value = DetailUiState(detail = d, isFavorite = fav)
            }.onFailure {
                _state.value = DetailUiState(error = it.message)
            }
        }
    }

    fun toggleFavorite() {
        viewModelScope.launch {
            val result = toggleFav(toiletId)
            _state.value = _state.value.copy(isFavorite = result)
        }
    }

    fun submitReview(
        rating: Int,
        cleanliness: Int,
        bidetWorks: Boolean,
        comment: String,
        photoUri: Uri?,
    ) {
        _state.value = _state.value.copy(submittingReview = true)
        viewModelScope.launch {
            runCatching {
                val urls = photoUri?.let { listOf(uploadPhoto("reviews/$toiletId", it)) } ?: emptyList()
                addReview(toiletId, rating, cleanliness, bidetWorks, comment, urls)
            }.onSuccess { load(toiletId) }
                .onFailure { _state.value = _state.value.copy(error = it.message) }
            _state.value = _state.value.copy(submittingReview = false)
        }
    }
}
