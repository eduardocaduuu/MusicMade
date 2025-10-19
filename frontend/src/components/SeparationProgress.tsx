import React, { useEffect, useState } from 'react';
import { apiClient } from '../services/api';
import { SeparationJob, JobStatus, JobStatusUpdate } from '../types';

interface SeparationProgressProps {
  jobId: string;
  onCompleted: (job: SeparationJob) => void;
}

const SeparationProgress: React.FC<SeparationProgressProps> = ({ jobId, onCompleted }) => {
  const [job, setJob] = useState<SeparationJob | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let ws: WebSocket | null = null;
    let pollInterval: NodeJS.Timeout | null = null;

    const fetchJobStatus = async () => {
      try {
        const jobData = await apiClient.getJobStatus(jobId);
        setJob(jobData);

        if (jobData.status === JobStatus.COMPLETED) {
          onCompleted(jobData);
          if (pollInterval) clearInterval(pollInterval);
        } else if (jobData.status === JobStatus.FAILED) {
          setError(jobData.error_message || 'Separation failed');
          if (pollInterval) clearInterval(pollInterval);
        }
      } catch (err: any) {
        setError('Failed to fetch job status');
      }
    };

    // Try WebSocket first, fallback to polling
    try {
      ws = apiClient.createJobWebSocket(jobId);

      ws.onmessage = (event) => {
        const update: JobStatusUpdate = JSON.parse(event.data);

        apiClient.getJobStatus(jobId).then((jobData) => {
          setJob(jobData);

          if (jobData.status === JobStatus.COMPLETED) {
            onCompleted(jobData);
          } else if (jobData.status === JobStatus.FAILED) {
            setError(jobData.error_message || 'Separation failed');
          }
        });
      };

      ws.onerror = () => {
        // Fallback to polling
        pollInterval = setInterval(fetchJobStatus, 2000);
      };
    } catch {
      // WebSocket not available, use polling
      pollInterval = setInterval(fetchJobStatus, 2000);
    }

    // Initial fetch
    fetchJobStatus();

    return () => {
      if (ws) ws.close();
      if (pollInterval) clearInterval(pollInterval);
    };
  }, [jobId, onCompleted]);

  if (error) {
    return (
      <div className="p-6 bg-red-50 border border-red-200 rounded-lg">
        <h3 className="text-lg font-semibold text-red-800 mb-2">Separation Failed</h3>
        <p className="text-red-600">{error}</p>
      </div>
    );
  }

  if (!job) {
    return (
      <div className="flex items-center justify-center p-6">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  const statusColors = {
    [JobStatus.PENDING]: 'bg-yellow-100 text-yellow-800',
    [JobStatus.PROCESSING]: 'bg-blue-100 text-blue-800',
    [JobStatus.COMPLETED]: 'bg-green-100 text-green-800',
    [JobStatus.FAILED]: 'bg-red-100 text-red-800',
  };

  return (
    <div className="w-full max-w-2xl mx-auto space-y-6">
      <div className="bg-white shadow-lg rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Separating Instruments</h3>
          <span
            className={`px-3 py-1 rounded-full text-xs font-medium ${
              statusColors[job.status]
            }`}
          >
            {job.status.toUpperCase()}
          </span>
        </div>

        <div className="space-y-4">
          <div>
            <div className="flex justify-between text-sm text-gray-600 mb-2">
              <span>Progress</span>
              <span>{Math.round(job.progress)}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div
                className="bg-primary-600 h-3 rounded-full transition-all duration-500"
                style={{ width: `${job.progress}%` }}
              ></div>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-600">Algorithm:</span>
              <span className="ml-2 font-medium">{job.algorithm}</span>
            </div>
            <div>
              <span className="text-gray-600">Quality:</span>
              <span className="ml-2 font-medium">{job.quality}</span>
            </div>
          </div>

          {job.status === JobStatus.PROCESSING && (
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary-600"></div>
              <span>Processing audio... This may take a few minutes.</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SeparationProgress;
