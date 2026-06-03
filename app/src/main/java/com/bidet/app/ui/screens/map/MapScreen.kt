package com.bidet.app.ui.screens.map

import android.util.Log
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.LocationOn
import androidx.compose.material.icons.filled.MyLocation
import androidx.compose.material.icons.filled.Person
import androidx.compose.material.icons.filled.Search
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.ExtendedFloatingActionButton
import androidx.compose.material3.FloatingActionButton
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.clickable
import androidx.hilt.navigation.compose.hiltViewModel
import com.bidet.app.BuildConfig
import com.bidet.app.data.model.Toilet
import com.bidet.app.util.rememberLocationPermissionState
import com.kakao.vectormap.KakaoMap
import com.kakao.vectormap.KakaoMapReadyCallback
import com.kakao.vectormap.LatLng as KakaoLatLng
import com.kakao.vectormap.MapLifeCycleCallback
import com.kakao.vectormap.MapView
import com.kakao.vectormap.camera.CameraUpdateFactory
import com.kakao.vectormap.label.LabelOptions
import com.kakao.vectormap.label.LabelStyle
import com.kakao.vectormap.label.LabelStyles
import com.kakao.vectormap.label.LabelTextBuilder

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MapScreen(
    onSearchClick: () -> Unit,
    onToiletClick: (String) -> Unit,
    onReportClick: () -> Unit,
    onProfileClick: () -> Unit,
    viewModel: MapViewModel = hiltViewModel(),
) {
    val state by viewModel.state.collectAsState()
    val context = LocalContext.current
    val permissionGranted by rememberLocationPermissionState()

    LaunchedEffect(permissionGranted) {
        if (permissionGranted) viewModel.centerOnCurrentLocation(context)
        else viewModel.loadNearby(state.center.lat, state.center.lng)
    }

    val hasKakaoKey = BuildConfig.KAKAO_NATIVE_APP_KEY.isNotBlank()

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Column {
                        Text("비데앱")
                        if (BuildConfig.DEMO_MODE) {
                            Text("DEMO 모드 · 더미 데이터",
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.tertiary)
                        }
                    }
                },
                actions = {
                    IconButton(onClick = onSearchClick) {
                        Icon(Icons.Default.Search, contentDescription = "검색")
                    }
                    IconButton(onClick = onProfileClick) {
                        Icon(Icons.Default.Person, contentDescription = "프로필")
                    }
                }
            )
        },
        floatingActionButton = {
            ExtendedFloatingActionButton(
                onClick = onReportClick,
                icon = { Icon(Icons.Default.Add, contentDescription = null) },
                text = { Text("제보") }
            )
        }
    ) { padding ->
        if (hasKakaoKey) {
            KakaoMapPane(
                state = state,
                onToiletClick = onToiletClick,
                onMyLocationClick = { viewModel.centerOnCurrentLocation(context) },
                modifier = Modifier.fillMaxSize().padding(padding),
            )
        } else {
            FallbackToiletList(
                toilets = state.toilets,
                onToiletClick = onToiletClick,
                contentPadding = padding,
            )
        }
    }
}

@Composable
private fun KakaoMapPane(
    state: MapUiState,
    onToiletClick: (String) -> Unit,
    onMyLocationClick: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val kakaoMapRef = remember { mutableStateOf<KakaoMap?>(null) }

    LaunchedEffect(state.cameraTrigger, kakaoMapRef.value) {
        kakaoMapRef.value?.moveCamera(
            CameraUpdateFactory.newCenterPosition(
                KakaoLatLng.from(state.center.lat, state.center.lng), 15
            )
        )
    }
    LaunchedEffect(state.toilets, kakaoMapRef.value) {
        kakaoMapRef.value?.let { renderMarkers(it, state.toilets, onToiletClick) }
    }

    Box(modifier = modifier) {
        AndroidView(
            modifier = Modifier.fillMaxSize(),
            factory = { ctx ->
                MapView(ctx).also { mv ->
                    mv.start(
                        object : MapLifeCycleCallback() {
                            override fun onMapDestroy() {}
                            override fun onMapError(error: Exception?) {
                                Log.e("MapScreen", "map error", error)
                            }
                        },
                        object : KakaoMapReadyCallback() {
                            override fun onMapReady(map: KakaoMap) { kakaoMapRef.value = map }
                        }
                    )
                }
            }
        )
        FloatingActionButton(
            onClick = onMyLocationClick,
            modifier = Modifier.align(Alignment.BottomStart).padding(16.dp),
        ) {
            Icon(Icons.Default.MyLocation, contentDescription = "현위치")
        }
    }
}

@Composable
private fun FallbackToiletList(
    toilets: List<Toilet>,
    onToiletClick: (String) -> Unit,
    contentPadding: PaddingValues,
) {
    Column(modifier = Modifier.fillMaxSize().padding(contentPadding)) {
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .background(MaterialTheme.colorScheme.tertiaryContainer)
                .padding(16.dp)
        ) {
            Column {
                Text("🗺️ 지도 미사용 모드 (카카오 키 미설정)",
                    style = MaterialTheme.typography.titleSmall,
                    fontWeight = FontWeight.Bold)
                Text("local.properties에 KAKAO_NATIVE_APP_KEY 입력하면 지도가 표시됩니다.",
                    style = MaterialTheme.typography.bodySmall)
            }
        }
        LazyColumn(
            modifier = Modifier.fillMaxSize().padding(horizontal = 16.dp, vertical = 8.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            items(toilets, key = { it.id }) { t ->
                ToiletCard(t, onClick = { onToiletClick(t.id) })
            }
        }
    }
}

@Composable
private fun ToiletCard(toilet: Toilet, onClick: () -> Unit) {
    Card(
        modifier = Modifier.fillMaxWidth().clickable { onClick() },
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
        shape = RoundedCornerShape(12.dp),
    ) {
        Row(modifier = Modifier.padding(16.dp), verticalAlignment = Alignment.CenterVertically) {
            Icon(
                Icons.Default.LocationOn,
                contentDescription = null,
                tint = if (toilet.bidetVerified) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.outline,
                modifier = Modifier.padding(end = 12.dp),
            )
            Column(modifier = Modifier.weight(1f)) {
                Text(toilet.name, fontWeight = FontWeight.SemiBold,
                    style = MaterialTheme.typography.bodyLarge)
                Text(toilet.address, style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant)
                Row {
                    Text("⭐ ${"%.1f".format(toilet.rating)}",
                        style = MaterialTheme.typography.bodySmall)
                    Spacer(Modifier.height(8.dp))
                    if (toilet.bidetVerified) {
                        Text("  ✓ 검증됨",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.primary)
                    }
                }
            }
        }
    }
}

private fun renderMarkers(
    map: KakaoMap,
    toilets: List<Toilet>,
    onMarkerClick: (String) -> Unit,
) {
    val layer = map.labelManager?.layer ?: return
    layer.removeAll()
    val styles = map.labelManager?.addLabelStyles(
        LabelStyles.from(LabelStyle.from(android.R.drawable.ic_menu_mylocation))
    )
    toilets.forEach { t ->
        val options = LabelOptions
            .from(KakaoLatLng.from(t.lat, t.lng))
            .setStyles(styles)
            .setTexts(LabelTextBuilder().setTexts(t.name))
        val label = layer.addLabel(options)
        label?.tag = t.id
    }
    map.setOnLabelClickListener { _, _, label ->
        (label.tag as? String)?.let(onMarkerClick)
        true
    }
}
