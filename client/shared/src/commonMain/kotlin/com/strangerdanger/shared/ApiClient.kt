package com.strangerdanger.shared

import io.ktor.client.HttpClient
import io.ktor.client.call.body
import io.ktor.client.request.get

class ApiClient(private val baseUrl: String, private val client: HttpClient) {
    suspend fun health(): Map<String, String> = client.get("$baseUrl/healthz").body()
}
