package com.bidet.app.data.demo

import com.bidet.app.data.model.DataSource
import com.bidet.app.data.model.GenderAvailability
import com.bidet.app.data.model.Review
import com.bidet.app.data.model.SourceType
import com.bidet.app.data.model.Toilet
import com.bidet.app.data.model.ToiletCategory

/**
 * 데모용 더미 데이터. 고려대 안암동 캠퍼스 주변 화장실.
 * 실제 비데 유무는 검증되지 않은 예시 데이터.
 */
object DemoData {

    private val now = System.currentTimeMillis()

    val toilets: List<Toilet> = listOf(
        Toilet(
            id = "demo-001",
            name = "고려대 중앙도서관",
            address = "서울 성북구 안암로 145 고려대학교 중앙도서관",
            lat = 37.5894, lng = 127.0327,
            geohash = "wydn3",
            category = ToiletCategory.UNIVERSITY,
            hasBidet = true, bidetVerified = true, bidetCount = 4,
            gender = GenderAvailability.BOTH, accessible = true,
            openHours = "06:00-24:00", isFree = true,
            rating = 4.5, reviewCount = 12,
            sources = listOf(DataSource(
                type = SourceType.USER_REPORT,
                description = "데모 시드 데이터",
                collectedAt = now
            )),
            createdAt = now, updatedAt = now,
        ),
        Toilet(
            id = "demo-002",
            name = "고려대 SK미래관",
            address = "서울 성북구 안암로 145 고려대학교 SK미래관",
            lat = 37.5871, lng = 127.0317,
            geohash = "wydn3",
            category = ToiletCategory.UNIVERSITY,
            hasBidet = true, bidetVerified = true, bidetCount = 6,
            gender = GenderAvailability.BOTH, accessible = true,
            openHours = "07:00-23:00", isFree = true,
            rating = 4.7, reviewCount = 23,
            sources = listOf(DataSource(SourceType.USER_REPORT, description = "데모", collectedAt = now)),
            createdAt = now, updatedAt = now,
        ),
        Toilet(
            id = "demo-003",
            name = "고려대 정경관",
            address = "서울 성북구 안암로 145 고려대학교 정경관",
            lat = 37.5907, lng = 127.0334,
            geohash = "wydn3",
            category = ToiletCategory.UNIVERSITY,
            hasBidet = true, bidetVerified = false, bidetCount = 2,
            gender = GenderAvailability.BOTH,
            openHours = "08:00-22:00", isFree = true,
            rating = 3.9, reviewCount = 5,
            sources = listOf(DataSource(SourceType.BLOG_REVIEW, url = "https://example.com/blog1", collectedAt = now)),
            createdAt = now, updatedAt = now,
        ),
        Toilet(
            id = "demo-004",
            name = "안암역 1번 출구 공중화장실",
            address = "서울 성북구 안암로 145 안암역",
            lat = 37.5867, lng = 127.0297,
            geohash = "wydn3",
            category = ToiletCategory.SUBWAY,
            hasBidet = true, bidetVerified = true,
            gender = GenderAvailability.BOTH, accessible = true,
            openHours = "05:30-24:30", is24h = false, isFree = true,
            rating = 3.5, reviewCount = 8,
            sources = listOf(DataSource(SourceType.PUBLIC_DATA, description = "서울교통공사 시설정보", collectedAt = now)),
            createdAt = now, updatedAt = now,
        ),
        Toilet(
            id = "demo-005",
            name = "스타벅스 안암역점",
            address = "서울 성북구 고려대로 110",
            lat = 37.5862, lng = 127.0290,
            geohash = "wydn3",
            category = ToiletCategory.CAFE,
            hasBidet = true, bidetVerified = true,
            gender = GenderAvailability.UNISEX,
            openHours = "07:00-23:00", isFree = false,
            rating = 4.2, reviewCount = 17,
            sources = listOf(DataSource(SourceType.MAP_REVIEW, url = "https://place.map.kakao.com/example", collectedAt = now)),
            createdAt = now, updatedAt = now,
        ),
        Toilet(
            id = "demo-006",
            name = "참살이길 GS25 화장실",
            address = "서울 성북구 안암로9길 25",
            lat = 37.5851, lng = 127.0320,
            geohash = "wydn3",
            category = ToiletCategory.ETC,
            hasBidet = true, bidetVerified = false,
            gender = GenderAvailability.UNISEX,
            openHours = "24시간", is24h = true, isFree = false,
            rating = 3.1, reviewCount = 3,
            sources = listOf(DataSource(SourceType.USER_REPORT, description = "사용자 제보", collectedAt = now)),
            createdAt = now, updatedAt = now,
        ),
        Toilet(
            id = "demo-007",
            name = "고려대학교 안암병원 1층",
            address = "서울 성북구 인촌로 73",
            lat = 37.5848, lng = 127.0270,
            geohash = "wydn3",
            category = ToiletCategory.HOSPITAL,
            hasBidet = true, bidetVerified = true, bidetCount = 10,
            gender = GenderAvailability.BOTH, accessible = true,
            openHours = "24시간", is24h = true, isFree = true,
            rating = 4.6, reviewCount = 31,
            sources = listOf(DataSource(SourceType.OFFICIAL_WEBSITE, url = "https://kumc.or.kr/anam", collectedAt = now)),
            createdAt = now, updatedAt = now,
        ),
        Toilet(
            id = "demo-008",
            name = "롯데마트 청량리점",
            address = "서울 동대문구 왕산로 214",
            lat = 37.5803, lng = 127.0463,
            geohash = "wydn3",
            category = ToiletCategory.MART,
            hasBidet = true, bidetVerified = true,
            gender = GenderAvailability.BOTH, accessible = true,
            openHours = "10:00-23:00", isFree = true,
            rating = 4.3, reviewCount = 19,
            sources = listOf(DataSource(SourceType.OFFICIAL_WEBSITE, url = "https://company.lottemart.com", collectedAt = now)),
            createdAt = now, updatedAt = now,
        ),
        Toilet(
            id = "demo-009",
            name = "성북구청 1층 민원실",
            address = "서울 성북구 보문로 168",
            lat = 37.5895, lng = 127.0167,
            geohash = "wydn3",
            category = ToiletCategory.GOVERNMENT,
            hasBidet = true, bidetVerified = true,
            gender = GenderAvailability.BOTH, accessible = true,
            openHours = "09:00-18:00 (주중)", isFree = true,
            rating = 4.1, reviewCount = 7,
            sources = listOf(DataSource(SourceType.INFORMATION_DISCLOSURE, description = "성북구청 정보공개청구 답변", collectedAt = now)),
            createdAt = now, updatedAt = now,
        ),
        Toilet(
            id = "demo-010",
            name = "서울시립대학교 중앙도서관",
            address = "서울 동대문구 서울시립대로 163",
            lat = 37.5839, lng = 127.0589,
            geohash = "wydn3",
            category = ToiletCategory.UNIVERSITY,
            hasBidet = true, bidetVerified = false,
            gender = GenderAvailability.BOTH,
            openHours = "08:00-22:00", isFree = true,
            rating = 3.8, reviewCount = 9,
            sources = listOf(DataSource(SourceType.BLOG_REVIEW, url = "https://blog.naver.com/example", collectedAt = now)),
            createdAt = now, updatedAt = now,
        ),
    )

    val reviews: Map<String, List<Review>> = mapOf(
        "demo-001" to listOf(
            Review(id = "r-001-1", toiletId = "demo-001", userId = "u1", userName = "도서관러",
                rating = 5, cleanliness = 5, bidetWorks = true,
                comment = "비데 깨끗하고 잘 작동해요. 시험기간엔 줄 섭니다.",
                createdAt = now - 86400000),
            Review(id = "r-001-2", toiletId = "demo-001", userId = "u2", userName = "고대생",
                rating = 4, cleanliness = 4, bidetWorks = true,
                comment = "지하 1층이 제일 깨끗함",
                createdAt = now - 172800000),
        ),
        "demo-002" to listOf(
            Review(id = "r-002-1", toiletId = "demo-002", userId = "u3", userName = "SK러",
                rating = 5, cleanliness = 5, bidetWorks = true,
                comment = "신축이라 진짜 깨끗함. 비데 최고.",
                createdAt = now - 43200000),
        ),
        "demo-005" to listOf(
            Review(id = "r-005-1", toiletId = "demo-005", userId = "u4", userName = "익명",
                rating = 4, cleanliness = 4, bidetWorks = true,
                comment = "스벅 화장실은 항상 믿고 가요",
                createdAt = now - 86400000),
        ),
    )
}
