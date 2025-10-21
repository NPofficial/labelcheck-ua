import {
  ApiResponse,
  ValidationResult,
  GenerateLabelRequest,
  GenerateLabelResponse,
  CheckLabelRequest,
} from "@/types/api"
import { API_ENDPOINTS } from "./constants"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

class ApiClient {
  private baseUrl: string

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl
  }

  private async request<T>(
    endpoint: string,
    options?: RequestInit
  ): Promise<ApiResponse<T>> {
    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        ...options,
        headers: {
          "Content-Type": "application/json",
          ...options?.headers,
        },
      })

      const data = await response.json()

      if (!response.ok) {
        return {
          success: false,
          error: data.message || "Щось пішло не так",
        }
      }

      return {
        success: true,
        data,
      }
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : "Помилка мережі",
      }
    }
  }

  async generateLabel(
    request: GenerateLabelRequest
  ): Promise<ApiResponse<GenerateLabelResponse>> {
    return this.request<GenerateLabelResponse>(API_ENDPOINTS.GENERATE_LABEL, {
      method: "POST",
      body: JSON.stringify(request),
    })
  }

  async checkLabel(file: File): Promise<ApiResponse<ValidationResult>> {
    const formData = new FormData()
    formData.append("file", file)

    try {
      const response = await fetch(`${this.baseUrl}${API_ENDPOINTS.CHECK_LABEL}`, {
        method: "POST",
        body: formData,
      })

      const data = await response.json()

      if (!response.ok) {
        return {
          success: false,
          error: data.message || "Щось пішло не так",
        }
      }

      return {
        success: true,
        data,
      }
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : "Помилка мережі",
      }
    }
  }

  async checkLabelText(text: string): Promise<ApiResponse<ValidationResult>> {
    return this.request<ValidationResult>(API_ENDPOINTS.CHECK_LABEL, {
      method: "POST",
      body: JSON.stringify({ text }),
    })
  }

  async getValidationResult(id: string): Promise<ApiResponse<ValidationResult>> {
    return this.request<ValidationResult>(`${API_ENDPOINTS.GET_RESULT}/${id}`, {
      method: "GET",
    })
  }
}

export const apiClient = new ApiClient(API_URL)

