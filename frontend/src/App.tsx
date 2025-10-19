import React, { useState } from 'react';
import AudioUpload from './components/AudioUpload';
import SeparationProgress from './components/SeparationProgress';
import InstrumentPlayer from './components/InstrumentPlayer';
import TablatureViewer from './components/TablatureViewer';
import {
  AudioFile,
  SeparationJob,
  Algorithm,
  Quality,
  SeparationJobCreate,
  Track,
} from './types';
import { apiClient } from './services/api';
import './App.css';

enum AppState {
  UPLOAD,
  CONFIGURE,
  PROCESSING,
  RESULTS,
}

function App() {
  const [appState, setAppState] = useState<AppState>(AppState.UPLOAD);
  const [audioFile, setAudioFile] = useState<AudioFile | null>(null);
  const [algorithm, setAlgorithm] = useState<Algorithm>(Algorithm.DEMUCS);
  const [quality, setQuality] = useState<Quality>(Quality.FAST);
  const [separationJob, setSeparationJob] = useState<SeparationJob | null>(null);
  const [selectedTrack, setSelectedTrack] = useState<Track | null>(null);

  const handleFileUploaded = (file: AudioFile) => {
    setAudioFile(file);
    setAppState(AppState.CONFIGURE);
  };

  const handleStartSeparation = async () => {
    if (!audioFile) return;

    try {
      const params: SeparationJobCreate = { algorithm, quality };
      const job = await apiClient.createSeparationJob(audioFile.id, params);
      setSeparationJob(job);
      setAppState(AppState.PROCESSING);
    } catch (error) {
      console.error('Failed to start separation:', error);
    }
  };

  const handleSeparationCompleted = (job: SeparationJob) => {
    setSeparationJob(job);
    setAppState(AppState.RESULTS);
  };

  const handleReset = () => {
    setAudioFile(null);
    setSeparationJob(null);
    setSelectedTrack(null);
    setAppState(AppState.UPLOAD);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">MusicMade</h1>
              <p className="text-sm text-gray-600 mt-1">
                AI-Powered Music Instrument Separator & Tablature Generator
              </p>
            </div>
            {appState !== AppState.UPLOAD && (
              <button
                onClick={handleReset}
                className="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-md font-medium transition-colors"
              >
                New Upload
              </button>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Upload State */}
        {appState === AppState.UPLOAD && (
          <div className="space-y-6">
            <div className="text-center mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-2">
                Upload Your Audio File
              </h2>
              <p className="text-gray-600">
                Start by uploading an audio file to separate instruments
              </p>
            </div>
            <AudioUpload onFileUploaded={handleFileUploaded} />
          </div>
        )}

        {/* Configuration State */}
        {appState === AppState.CONFIGURE && audioFile && (
          <div className="max-w-2xl mx-auto space-y-6">
            <div className="bg-white shadow-lg rounded-lg p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                Configure Separation
              </h2>

              <div className="space-y-4">
                <div className="bg-gray-50 p-4 rounded-md">
                  <h3 className="font-medium text-gray-900 mb-2">Uploaded File</h3>
                  <p className="text-sm text-gray-600">{audioFile.filename}</p>
                  <p className="text-xs text-gray-500 mt-1">
                    Duration: {audioFile.duration?.toFixed(2)}s | Size:{' '}
                    {(audioFile.file_size / 1024 / 1024).toFixed(2)}MB
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Algorithm
                  </label>
                  <select
                    value={algorithm}
                    onChange={(e) => setAlgorithm(e.target.value as Algorithm)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                  >
                    <option value={Algorithm.DEMUCS}>
                      Demucs (Recommended - Best Quality)
                    </option>
                    <option value={Algorithm.SPLEETER}>Spleeter (Faster)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Quality
                  </label>
                  <select
                    value={quality}
                    onChange={(e) => setQuality(e.target.value as Quality)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                  >
                    <option value={Quality.FAST}>Fast (Quicker processing)</option>
                    <option value={Quality.HIGH}>High Quality (Better results)</option>
                  </select>
                </div>

                <button
                  onClick={handleStartSeparation}
                  className="w-full px-4 py-3 bg-primary-600 hover:bg-primary-700 text-white rounded-md font-medium text-lg transition-colors"
                >
                  Start Separation
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Processing State */}
        {appState === AppState.PROCESSING && separationJob && (
          <div className="space-y-6">
            <div className="text-center mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-2">
                Processing Your Audio
              </h2>
              <p className="text-gray-600">
                This may take a few minutes depending on the file size
              </p>
            </div>
            <SeparationProgress
              jobId={separationJob.id}
              onCompleted={handleSeparationCompleted}
            />
          </div>
        )}

        {/* Results State */}
        {appState === AppState.RESULTS && separationJob && (
          <div className="space-y-8">
            <div className="text-center mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-2">
                Separation Complete!
              </h2>
              <p className="text-gray-600">
                {separationJob.tracks.length} instruments have been separated
              </p>
            </div>

            {/* Audio Player */}
            <InstrumentPlayer tracks={separationJob.tracks} />

            {/* Track Selection for Tablature */}
            <div className="bg-white shadow-lg rounded-lg p-6">
              <h3 className="text-xl font-semibold text-gray-900 mb-4">
                Generate Tablature
              </h3>
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
                {separationJob.tracks.map((track) => (
                  <button
                    key={track.id}
                    onClick={() => setSelectedTrack(track)}
                    className={`px-4 py-3 rounded-lg font-medium capitalize transition-all ${
                      selectedTrack?.id === track.id
                        ? 'bg-primary-600 text-white shadow-lg'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    {track.instrument_name}
                  </button>
                ))}
              </div>
            </div>

            {/* Tablature Viewer */}
            {selectedTrack && <TablatureViewer track={selectedTrack} />}
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-sm text-gray-600">
            Made with AI-powered audio separation technology
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
