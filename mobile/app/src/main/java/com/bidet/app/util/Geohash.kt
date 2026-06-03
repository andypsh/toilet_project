package com.bidet.app.util

import kotlin.math.cos
import kotlin.math.sqrt

object Geohash {
    fun encode(lat: Double, lng: Double, precision: Int = 9): String {
        val base32 = "0123456789bcdefghjkmnpqrstuvwxyz"
        var latRange = doubleArrayOf(-90.0, 90.0)
        var lngRange = doubleArrayOf(-180.0, 180.0)
        val sb = StringBuilder()
        var isEven = true
        var bit = 0
        var ch = 0
        while (sb.length < precision) {
            if (isEven) {
                val mid = (lngRange[0] + lngRange[1]) / 2
                if (lng >= mid) { ch = ch or (1 shl (4 - bit)); lngRange[0] = mid }
                else lngRange[1] = mid
            } else {
                val mid = (latRange[0] + latRange[1]) / 2
                if (lat >= mid) { ch = ch or (1 shl (4 - bit)); latRange[0] = mid }
                else latRange[1] = mid
            }
            isEven = !isEven
            if (bit < 4) bit++
            else { sb.append(base32[ch]); bit = 0; ch = 0 }
        }
        return sb.toString()
    }

    fun boundsForRadius(lat: Double, lng: Double, radiusKm: Double): Pair<String, String> {
        val precision = when {
            radiusKm < 0.5 -> 7
            radiusKm < 2.0 -> 6
            radiusKm < 20.0 -> 5
            else -> 4
        }
        val center = encode(lat, lng, precision)
        return center to center + "~"
    }

    fun distanceKm(lat1: Double, lng1: Double, lat2: Double, lng2: Double): Double {
        val r = 6371.0
        val dLat = Math.toRadians(lat2 - lat1)
        val dLng = Math.toRadians(lng2 - lng1)
        val a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
                Math.cos(Math.toRadians(lat1)) * Math.cos(Math.toRadians(lat2)) *
                Math.sin(dLng / 2) * Math.sin(dLng / 2)
        return r * 2 * Math.atan2(sqrt(a), sqrt(1 - a))
    }

    @Suppress("unused")
    private fun unusedCosCheck(x: Double) = cos(x)
}
