package com.bidet.app.ui.screens.search

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.bidet.app.data.model.Toilet
import com.bidet.app.domain.usecase.SearchToiletsUseCase
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

data class SearchUiState(
    val query: String = "",
    val results: List<Toilet> = emptyList(),
    val loading: Boolean = false,
)

@HiltViewModel
class SearchViewModel @Inject constructor(
    private val search: SearchToiletsUseCase,
) : ViewModel() {

    private val _state = MutableStateFlow(SearchUiState())
    val state: StateFlow<SearchUiState> = _state.asStateFlow()

    fun onQueryChange(q: String) {
        _state.value = _state.value.copy(query = q)
    }

    fun submit() {
        val q = _state.value.query
        _state.value = _state.value.copy(loading = true)
        viewModelScope.launch {
            val r = runCatching { search(q) }.getOrDefault(emptyList())
            _state.value = _state.value.copy(loading = false, results = r)
        }
    }
}
