package com.bidet.app.ui.preview

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.LocationOn
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import com.bidet.app.data.demo.DemoData
import com.bidet.app.data.model.Toilet
import com.bidet.app.ui.theme.BidetAppTheme

/**
 * Android Studio Compose Preview 모음.
 *
 * 이 파일의 @Preview 들은 Android Studio 의 Split / Design 뷰에서
 * 빌드 없이 즉시 렌더링됩니다.
 *
 * 친구 (UI 작업) 가이드:
 *  - mobile/app/src/main/java/com/bidet/app/ui/screens/(화면)/(파일).kt 를 열면
 *    파일 안의 @Preview composable 이 우측 패널에 그려집니다.
 *  - 새 컴포넌트 만들 때는 이 파일을 참고해서 같이 @Preview 추가하기.
 *  - 데이터는 com.bidet.app.data.demo.DemoData 활용.
 */

// ───────── 화장실 카드 (지도 fallback 리스트 항목) ─────────
@Composable
fun ToiletCardPreviewBody(toilet: Toilet) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
        shape = RoundedCornerShape(12.dp),
    ) {
        Row(modifier = Modifier.padding(16.dp), verticalAlignment = Alignment.CenterVertically) {
            Icon(
                Icons.Default.LocationOn,
                contentDescription = null,
                tint = if (toilet.bidetVerified) MaterialTheme.colorScheme.primary
                       else MaterialTheme.colorScheme.outline,
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

@Preview(name = "ToiletCard · 검증됨", showBackground = true, widthDp = 360)
@Composable
private fun ToiletCardVerifiedPreview() {
    BidetAppTheme {
        Surface { ToiletCardPreviewBody(DemoData.toilets[0]) }
    }
}

@Preview(name = "ToiletCard · 미검증", showBackground = true, widthDp = 360)
@Composable
private fun ToiletCardUnverifiedPreview() {
    BidetAppTheme {
        Surface { ToiletCardPreviewBody(DemoData.toilets[2]) }
    }
}

@Preview(name = "ToiletCard · 다크모드", showBackground = true, widthDp = 360)
@Composable
private fun ToiletCardDarkPreview() {
    BidetAppTheme(darkTheme = true) {
        Surface { ToiletCardPreviewBody(DemoData.toilets[1]) }
    }
}

// ───────── 카드 리스트 (지도 미사용 fallback 전체 모드) ─────────
@Preview(name = "ToiletCard List · 라이트", showBackground = true,
         widthDp = 360, heightDp = 720)
@Composable
private fun ToiletListLightPreview() {
    BidetAppTheme {
        Surface {
            LazyColumn(
                contentPadding = androidx.compose.foundation.layout.PaddingValues(16.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                items(DemoData.toilets, key = { it.id }) {
                    ToiletCardPreviewBody(it)
                }
            }
        }
    }
}

@Preview(name = "ToiletCard List · 다크", showBackground = true,
         widthDp = 360, heightDp = 720)
@Composable
private fun ToiletListDarkPreview() {
    BidetAppTheme(darkTheme = true) {
        Surface {
            LazyColumn(
                contentPadding = androidx.compose.foundation.layout.PaddingValues(16.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                items(DemoData.toilets, key = { it.id }) {
                    ToiletCardPreviewBody(it)
                }
            }
        }
    }
}

// ───────── 상세 화면 정보 블록 (출처 표시 — 팩트 추적 핵심 UI) ─────────
@Composable
fun ToiletInfoBlockPreviewBody(toilet: Toilet) {
    Column(modifier = Modifier.padding(16.dp)) {
        Text(toilet.name, style = MaterialTheme.typography.titleLarge,
             fontWeight = FontWeight.Bold)
        Text(toilet.address, style = MaterialTheme.typography.bodyLarge)
        Spacer(Modifier.height(8.dp))
        Text("비데: ${if (toilet.hasBidet) "✓ 있음" else "✗ 없음"}" +
                if (toilet.bidetVerified) " (검증됨)" else "")
        Text("운영시간: ${toilet.openHours ?: "정보 없음"}")
        Text("평점: ${"%.1f".format(toilet.rating)} (${toilet.reviewCount}건)")
        Spacer(Modifier.height(16.dp))
        Text("출처", style = MaterialTheme.typography.titleMedium)
        toilet.sources.forEach { src ->
            Text("• ${src.type.name} ${src.url ?: ""}",
                style = MaterialTheme.typography.bodySmall)
            src.description?.let {
                Text("    └ $it",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant)
            }
        }
    }
}

@Preview(name = "Detail · 검증된 비데", showBackground = true,
         widthDp = 380, heightDp = 480)
@Composable
private fun DetailVerifiedPreview() {
    BidetAppTheme {
        Surface { ToiletInfoBlockPreviewBody(DemoData.toilets[0]) }
    }
}

@Preview(name = "Detail · 블로그 출처", showBackground = true,
         widthDp = 380, heightDp = 480)
@Composable
private fun DetailBlogPreview() {
    BidetAppTheme {
        Surface { ToiletInfoBlockPreviewBody(DemoData.toilets[2]) }
    }
}
