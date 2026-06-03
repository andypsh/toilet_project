package com.bidet.app.ui.screens.map

import android.content.Context
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.bidet.app.BuildConfig
import com.bidet.app.data.model.Toilet
import com.bidet.app.domain.usecase.GetNearbyToiletsUseCase
import com.bidet.app.util.LatLng
import com.bidet.app.util.LocationHelper
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

data class MapUiState(
    val loading: Boolean = false,
    val toilets: List<Toilet> = emptyList(),
    // DEMO_MODE 일 때는 데모 데이터(고대 안암) 중심, 운영 모드는 서울시청
    val center: LatLng =
        if (BuildConfig.DEMO_MODE) LocationHelper.KOREA_UNIV_ANAM
        else LocationHelper.SEOUL_CITY_HALL,
    val cameraTrigger: Long = 0L,
    val error: String? = null,
)

@HiltViewModel
class MapViewModel @Inject constructor(
    private val getNearbyToilets: GetNearbyToiletsUseCase,
) : ViewModel() {

    private val _state = MutableStateFlow(MapUiState())
    val state: StateFlow<MapUiState> = _state.asStateFlow()

    fun centerOnCurrentLocation(context: Context) {
        viewModelScope.launch {
            val loc = LocationHelper.getCurrent(context) ?: LocationHelper.SEOUL_CITY_HALL
            _state.update {
                it.copy(center = loc, cameraTrigger = System.currentTimeMillis())
            }
            loadNearby(loc.lat, loc.lng)
        }
    }

    fun loadNearby(lat: Double, lng: Double, radiusKm: Double = 2.0) {
        _state.update { it.copy(loading = true, error = null) }
        viewModelScope.launch {
            runCatching { getNearbyToilets(lat, lng, radiusKm) }
                .onSuccess { list -> _state.update { it.copy(loading = false, toilets = list) } }
                .onFailure { e -> _state.update { it.copy(loading = false, error = e.message) } }
        }
    }
}
