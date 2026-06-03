package com.bidet.app.data.remote

import retrofit2.http.GET
import retrofit2.http.Header
import retrofit2.http.Query

interface KakaoLocalApi {
    @GET("v2/local/search/keyword.json")
    suspend fun searchKeyword(
        @Header("Authorization") auth: String,
        @Query("query") query: String,
        @Query("x") lng: Double? = null,
        @Query("y") lat: Double? = null,
        @Query("radius") radius: Int? = null,
        @Query("page") page: Int = 1,
        @Query("size") size: Int = 15,
    ): KakaoKeywordResponse

    @GET("v2/local/search/address.json")
    suspend fun searchAddress(
        @Header("Authorization") auth: String,
        @Query("query") query: String,
    ): KakaoAddressResponse
}

data class KakaoKeywordResponse(
    val documents: List<KakaoPlace> = emptyList(),
    val meta: KakaoMeta = KakaoMeta(),
)

data class KakaoPlace(
    val id: String = "",
    val place_name: String = "",
    val address_name: String = "",
    val road_address_name: String = "",
    val category_name: String = "",
    val x: String = "",
    val y: String = "",
)

data class KakaoAddressResponse(
    val documents: List<KakaoAddressDoc> = emptyList(),
)

data class KakaoAddressDoc(
    val address_name: String = "",
    val x: String = "",
    val y: String = "",
)

data class KakaoMeta(
    val total_count: Int = 0,
    val is_end: Boolean = true,
)
