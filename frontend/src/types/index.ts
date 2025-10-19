// Type definitions for MusicMade frontend

export interface AudioFile {
  id: string;
  filename: string;
  duration: number | null;
  sample_rate: number | null;
  channels: number | null;
  file_size: number;
  format: string | null;
  upload_date: string;
}

export enum JobStatus {
  PENDING = 'pending',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  FAILED = 'failed',
}

export enum Algorithm {
  DEMUCS = 'demucs',
  SPLEETER = 'spleeter',
}

export enum Quality {
  FAST = 'fast',
  HIGH = 'high',
}

export interface Track {
  id: string;
  separation_job_id: string;
  instrument_name: string;
  duration: number | null;
  file_size: number | null;
}

export interface SeparationJob {
  id: string;
  audio_file_id: string;
  status: JobStatus;
  algorithm: string;
  quality: string;
  progress: number;
  error_message: string | null;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
  tracks: Track[];
}

export interface SeparationJobCreate {
  algorithm: Algorithm;
  quality: Quality;
}

export enum InstrumentType {
  GUITAR = 'guitar',
  BASS = 'bass',
  PIANO = 'piano',
}

export interface TablatureCreate {
  instrument_type: InstrumentType;
  tuning: string;
}

export interface Tablature {
  id: string;
  track_id: string;
  instrument_type: string;
  tuning: string;
  content: string;
  created_at: string;
}

export interface JobStatusUpdate {
  job_id: string;
  status: JobStatus;
  progress: number;
  error_message: string | null;
}
