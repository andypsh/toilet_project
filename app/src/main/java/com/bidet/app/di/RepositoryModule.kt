package com.bidet.app.di

import com.bidet.app.BuildConfig
import com.bidet.app.data.demo.FakeAuthRepository
import com.bidet.app.data.demo.FakeReportRepository
import com.bidet.app.data.demo.FakeToiletRepository
import com.bidet.app.data.repository.AuthRepository
import com.bidet.app.data.repository.AuthRepositoryImpl
import com.bidet.app.data.repository.ReportRepository
import com.bidet.app.data.repository.ReportRepositoryImpl
import com.bidet.app.data.repository.ToiletRepository
import com.bidet.app.data.repository.ToiletRepositoryImpl
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import javax.inject.Provider
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object RepositoryModule {

    @Provides @Singleton
    fun provideToiletRepository(
        realProvider: Provider<ToiletRepositoryImpl>,
        fakeProvider: Provider<FakeToiletRepository>,
    ): ToiletRepository =
        if (BuildConfig.DEMO_MODE) fakeProvider.get() else realProvider.get()

    @Provides @Singleton
    fun provideAuthRepository(
        realProvider: Provider<AuthRepositoryImpl>,
        fakeProvider: Provider<FakeAuthRepository>,
    ): AuthRepository =
        if (BuildConfig.DEMO_MODE) fakeProvider.get() else realProvider.get()

    @Provides @Singleton
    fun provideReportRepository(
        realProvider: Provider<ReportRepositoryImpl>,
        fakeProvider: Provider<FakeReportRepository>,
    ): ReportRepository =
        if (BuildConfig.DEMO_MODE) fakeProvider.get() else realProvider.get()
}
