package com.bidet.app.domain.usecase

import android.net.Uri
import com.bidet.app.data.remote.FirebaseStorageSource
import javax.inject.Inject

class UploadPhotoUseCase @Inject constructor(
    private val storage: FirebaseStorageSource
) {
    suspend operator fun invoke(folder: String, uri: Uri): String {
        val path = "$folder/${System.currentTimeMillis()}_${(0..9999).random()}.jpg"
        return storage.uploadImage(path, uri)
    }
}
