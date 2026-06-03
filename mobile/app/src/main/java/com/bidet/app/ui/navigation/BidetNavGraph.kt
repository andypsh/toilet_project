package com.bidet.app.ui.navigation

import androidx.compose.runtime.Composable
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.navigation.NavType
import androidx.navigation.navArgument
import com.bidet.app.ui.screens.auth.AuthScreen
import com.bidet.app.ui.screens.detail.ToiletDetailScreen
import com.bidet.app.ui.screens.map.MapScreen
import com.bidet.app.ui.screens.profile.ProfileScreen
import com.bidet.app.ui.screens.report.ReportScreen
import com.bidet.app.ui.screens.search.SearchScreen

object Routes {
    const val MAP = "map"
    const val SEARCH = "search"
    const val DETAIL = "detail/{toiletId}"
    const val REPORT = "report"
    const val PROFILE = "profile"
    const val AUTH = "auth"

    fun detail(toiletId: String) = "detail/$toiletId"
}

@Composable
fun BidetNavGraph() {
    val nav = rememberNavController()
    NavHost(navController = nav, startDestination = Routes.MAP) {
        composable(Routes.MAP) {
            MapScreen(
                onSearchClick = { nav.navigate(Routes.SEARCH) },
                onToiletClick = { id -> nav.navigate(Routes.detail(id)) },
                onReportClick = { nav.navigate(Routes.REPORT) },
                onProfileClick = { nav.navigate(Routes.PROFILE) },
            )
        }
        composable(Routes.SEARCH) {
            SearchScreen(
                onBack = { nav.popBackStack() },
                onToiletClick = { id -> nav.navigate(Routes.detail(id)) },
            )
        }
        composable(
            Routes.DETAIL,
            arguments = listOf(navArgument("toiletId") { type = NavType.StringType })
        ) { backStack ->
            val id = backStack.arguments?.getString("toiletId").orEmpty()
            ToiletDetailScreen(toiletId = id, onBack = { nav.popBackStack() })
        }
        composable(Routes.REPORT) {
            ReportScreen(onBack = { nav.popBackStack() })
        }
        composable(Routes.PROFILE) {
            ProfileScreen(
                onBack = { nav.popBackStack() },
                onSignInRequired = { nav.navigate(Routes.AUTH) },
            )
        }
        composable(Routes.AUTH) {
            AuthScreen(onSignedIn = { nav.popBackStack() })
        }
    }
}
