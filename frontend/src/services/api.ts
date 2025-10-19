/**
 * API client for MusicMade backend
 */
import axios, { AxiosInstance } from 'axios';
import {
  AudioFile,
  SeparationJob,
  SeparationJobCreate,
  Track,
  Tablature,
  TablatureCreate,
} from '../types';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  // Upload endpoints
  async uploadFile(file: File): Promise<AudioFile> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await this.client.post<AudioFile>('/api/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  }

  async getAudioFile(fileId: string): Promise<AudioFile> {
    const response = await this.client.get<AudioFile>(`/api/files/${fileId}`);
    return response.data;
  }

  async deleteAudioFile(fileId: string): Promise<void> {
    await this.client.delete(`/api/files/${fileId}`);
  }

  // Separation endpoints
  async createSeparationJob(
    fileId: string,
    params: SeparationJobCreate
  ): Promise<SeparationJob> {
    const response = await this.client.post<SeparationJob>(
      `/api/separate/${fileId}`,
      params
    );
    return response.data;
  }

  async getJobStatus(jobId: string): Promise<SeparationJob> {
    const response = await this.client.get<SeparationJob>(`/api/jobs/${jobId}`);
    return response.data;
  }

  async deleteJob(jobId: string): Promise<void> {
    await this.client.delete(`/api/jobs/${jobId}`);
  }

  async listJobs(): Promise<SeparationJob[]> {
    const response = await this.client.get<SeparationJob[]>('/api/jobs');
    return response.data;
  }

  // Track endpoints
  async getTrackInfo(trackId: string): Promise<Track> {
    const response = await this.client.get<Track>(`/api/tracks/${trackId}`);
    return response.data;
  }

  getTrackDownloadUrl(trackId: string): string {
    return `${API_URL}/api/tracks/${trackId}/download`;
  }

  getTrackStreamUrl(trackId: string): string {
    return `${API_URL}/api/tracks/${trackId}/stream`;
  }

  // Tablature endpoints
  async generateTablature(
    trackId: string,
    params: TablatureCreate
  ): Promise<Tablature> {
    const response = await this.client.post<Tablature>(
      `/api/tracks/${trackId}/tablature`,
      params
    );
    return response.data;
  }

  async getTablature(tablatureId: string): Promise<Tablature> {
    const response = await this.client.get<Tablature>(`/api/tablature/${tablatureId}`);
    return response.data;
  }

  async listTrackTablatures(trackId: string): Promise<Tablature[]> {
    const response = await this.client.get<Tablature[]>(
      `/api/tracks/${trackId}/tablatures`
    );
    return response.data;
  }

  async deleteTablature(tablatureId: string): Promise<void> {
    await this.client.delete(`/api/tablature/${tablatureId}`);
  }

  // WebSocket for job status updates
  createJobWebSocket(jobId: string): WebSocket {
    const wsUrl = process.env.REACT_APP_WS_URL || 'ws://localhost:8000';
    return new WebSocket(`${wsUrl}/api/jobs/${jobId}/ws`);
  }
}

export const apiClient = new ApiClient();
export default apiClient;
