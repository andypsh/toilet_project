package com.bidet.app.ui.screens.detail

import android.content.Intent
import android.net.Uri
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.PickVisualMediaRequest
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Directions
import androidx.compose.material.icons.filled.Favorite
import androidx.compose.material.icons.filled.FavoriteBorder
import androidx.compose.material.icons.filled.RateReview
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FloatingActionButton
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ToiletDetailScreen(
    toiletId: String,
    onBack: () -> Unit,
    viewModel: ToiletDetailViewModel = hiltViewModel(),
) {
    val state by viewModel.state.collectAsState()
    val context = LocalContext.current
    var showReviewDialog by remember { mutableStateOf(false) }

    LaunchedEffect(toiletId) { viewModel.load(toiletId) }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(state.detail?.toilet?.name ?: "상세") },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "뒤로")
                    }
                },
                actions = {
                    IconButton(onClick = viewModel::toggleFavorite) {
                        Icon(
                            if (state.isFavorite) Icons.Default.Favorite else Icons.Default.FavoriteBorder,
                            contentDescription = "즐겨찾기"
                        )
                    }
                }
            )
        },
        floatingActionButton = {
            FloatingActionButton(onClick = { showReviewDialog = true }) {
                Icon(Icons.Default.RateReview, contentDescription = "리뷰 작성")
            }
        }
    ) { padding ->
        val t = state.detail?.toilet
        if (t == null) {
            Text("로딩 중...", modifier = Modifier.padding(padding).padding(16.dp))
            return@Scaffold
        }
        LazyColumn(modifier = Modifier.fillMaxSize().padding(padding).padding(16.dp)) {
            item {
                Text(t.address, style = MaterialTheme.typography.bodyLarge)
                Spacer(Modifier.height(8.dp))
                Text("비데: ${if (t.hasBidet) "✓ 있음" else "✗ 없음"}" +
                        if (t.bidetVerified) " (검증됨)" else "")
                Text("운영시간: ${t.openHours ?: "정보 없음"}")
                Text("평점: ${"%.1f".format(t.rating)} (${t.reviewCount}건)")
                Spacer(Modifier.height(12.dp))
                Button(
                    onClick = { openDirections(context, t.lat, t.lng, t.name) },
                    modifier = Modifier.fillMaxWidth(),
                ) {
                    Icon(Icons.Default.Directions, contentDescription = null)
                    Spacer(Modifier.height(4.dp))
                    Text("  길찾기 (카카오맵)")
                }
                Spacer(Modifier.height(16.dp))
                Text("출처", style = MaterialTheme.typography.titleMedium)
                t.sources.forEach { src ->
                    Text("• ${src.type.name} ${src.url ?: ""}",
                        style = MaterialTheme.typography.bodySmall)
                }
                Spacer(Modifier.height(16.dp))
                Text("리뷰 (${state.detail?.reviews?.size ?: 0})", style = MaterialTheme.typography.titleMedium)
            }
            items(state.detail?.reviews ?: emptyList()) { r ->
                Card(modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp)) {
                    Column(modifier = Modifier.padding(12.dp)) {
                        Text("${r.userName} · ⭐ ${r.rating}")
                        Text("청결도 ${r.cleanliness}/5 · 비데 ${if (r.bidetWorks) "작동" else "고장"}")
                        Text(r.comment)
                    }
                }
            }
        }
    }

    if (showReviewDialog) {
        ReviewDialog(
            onDismiss = { showReviewDialog = false },
            onSubmit = { rating, cleanliness, works, comment, uri ->
                viewModel.submitReview(rating, cleanliness, works, comment, uri)
                showReviewDialog = false
            },
            submitting = state.submittingReview,
        )
    }
}

@Composable
private fun ReviewDialog(
    onDismiss: () -> Unit,
    onSubmit: (rating: Int, cleanliness: Int, bidetWorks: Boolean, comment: String, photo: Uri?) -> Unit,
    submitting: Boolean,
) {
    var rating by remember { mutableStateOf(5) }
    var cleanliness by remember { mutableStateOf(5) }
    var bidetWorks by remember { mutableStateOf(true) }
    var comment by remember { mutableStateOf("") }
    var photoUri by remember { mutableStateOf<Uri?>(null) }

    val photoPicker = rememberLauncherForActivityResult(
        ActivityResultContracts.PickVisualMedia()
    ) { uri -> photoUri = uri }

    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("리뷰 작성") },
        text = {
            Column {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text("평점")
                    Spacer(Modifier.height(8.dp))
                    (1..5).forEach { i ->
                        TextButton(onClick = { rating = i }) {
                            Text(if (i <= rating) "★" else "☆")
                        }
                    }
                }
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text("청결도")
                    Spacer(Modifier.height(8.dp))
                    (1..5).forEach { i ->
                        TextButton(onClick = { cleanliness = i }) {
                            Text(if (i <= cleanliness) "★" else "☆")
                        }
                    }
                }
                Row(verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.SpaceBetween,
                    modifier = Modifier.fillMaxWidth()) {
                    Text("비데 작동")
                    Switch(checked = bidetWorks, onCheckedChange = { bidetWorks = it })
                }
                OutlinedTextField(
                    value = comment,
                    onValueChange = { comment = it },
                    label = { Text("코멘트") },
                    modifier = Modifier.fillMaxWidth(),
                )
                TextButton(onClick = {
                    photoPicker.launch(PickVisualMediaRequest(
                        ActivityResultContracts.PickVisualMedia.ImageOnly
                    ))
                }) {
                    Text(if (photoUri == null) "사진 첨부" else "사진 첨부됨 ✓")
                }
            }
        },
        confirmButton = {
            Button(
                onClick = { onSubmit(rating, cleanliness, bidetWorks, comment, photoUri) },
                enabled = !submitting,
            ) { Text(if (submitting) "전송 중..." else "등록") }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) { Text("취소") }
        }
    )
}

private fun openDirections(context: android.content.Context, lat: Double, lng: Double, name: String) {
    val uri = Uri.parse("kakaomap://route?ep=$lat,$lng&by=FOOT")
    val intent = Intent(Intent.ACTION_VIEW, uri)
    val resolved = intent.resolveActivity(context.packageManager) != null
    if (resolved) {
        context.startActivity(intent)
    } else {
        // 카카오맵 없으면 웹 카카오맵으로
        val web = Intent(Intent.ACTION_VIEW,
            Uri.parse("https://map.kakao.com/link/to/$name,$lat,$lng"))
        context.startActivity(web)
    }
}
