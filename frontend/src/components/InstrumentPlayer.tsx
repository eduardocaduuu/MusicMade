import React, { useEffect, useRef, useState } from 'react';
import WaveSurfer from 'wavesurfer.js';
import { Track } from '../types';
import { apiClient } from '../services/api';

interface InstrumentPlayerProps {
  tracks: Track[];
}

interface TrackState {
  wavesurfer: WaveSurfer | null;
  volume: number;
  muted: boolean;
  solo: boolean;
}

const InstrumentPlayer: React.FC<InstrumentPlayerProps> = ({ tracks }) => {
  const [trackStates, setTrackStates] = useState<Map<string, TrackState>>(new Map());
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const containerRefs = useRef<Map<string, HTMLDivElement>>(new Map());

  useEffect(() => {
    // Initialize WaveSurfer for each track
    const newStates = new Map<string, TrackState>();

    tracks.forEach((track) => {
      const container = containerRefs.current.get(track.id);
      if (!container) return;

      const wavesurfer = WaveSurfer.create({
        container,
        waveColor: '#60a5fa',
        progressColor: '#2563eb',
        cursorColor: '#1e40af',
        height: 60,
        normalize: true,
        backend: 'WebAudio',
      });

      wavesurfer.load(apiClient.getTrackStreamUrl(track.id));

      wavesurfer.on('ready', () => {
        setDuration(wavesurfer.getDuration());
      });

      wavesurfer.on('audioprocess', () => {
        setCurrentTime(wavesurfer.getCurrentTime());
      });

      newStates.set(track.id, {
        wavesurfer,
        volume: 80,
        muted: false,
        solo: false,
      });
    });

    setTrackStates(newStates);

    return () => {
      newStates.forEach((state) => state.wavesurfer?.destroy());
    };
  }, [tracks]);

  const togglePlayPause = () => {
    trackStates.forEach((state) => {
      if (state.wavesurfer) {
        state.wavesurfer.playPause();
      }
    });
    setIsPlaying(!isPlaying);
  };

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const seekTime = parseFloat(e.target.value);
    trackStates.forEach((state) => {
      if (state.wavesurfer) {
        state.wavesurfer.seekTo(seekTime / duration);
      }
    });
  };

  const handleVolumeChange = (trackId: string, volume: number) => {
    const state = trackStates.get(trackId);
    if (state?.wavesurfer) {
      state.wavesurfer.setVolume(volume / 100);
      setTrackStates(
        new Map(trackStates.set(trackId, { ...state, volume }))
      );
    }
  };

  const toggleMute = (trackId: string) => {
    const state = trackStates.get(trackId);
    if (state?.wavesurfer) {
      const newMuted = !state.muted;
      state.wavesurfer.setVolume(newMuted ? 0 : state.volume / 100);
      setTrackStates(
        new Map(trackStates.set(trackId, { ...state, muted: newMuted }))
      );
    }
  };

  const toggleSolo = (trackId: string) => {
    const state = trackStates.get(trackId);
    if (!state) return;

    const newSolo = !state.solo;

    trackStates.forEach((s, id) => {
      if (s.wavesurfer) {
        if (id === trackId) {
          s.wavesurfer.setVolume(s.volume / 100);
          setTrackStates(
            new Map(trackStates.set(id, { ...s, solo: newSolo, muted: false }))
          );
        } else {
          s.wavesurfer.setVolume(newSolo ? 0 : s.volume / 100);
          setTrackStates(
            new Map(trackStates.set(id, { ...s, muted: newSolo }))
          );
        }
      }
    });
  };

  const downloadTrack = (trackId: string, instrumentName: string) => {
    const url = apiClient.getTrackDownloadUrl(trackId);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${instrumentName}.wav`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="w-full max-w-4xl mx-auto space-y-6">
      {/* Main Controls */}
      <div className="bg-white shadow-lg rounded-lg p-6">
        <div className="flex items-center space-x-4 mb-4">
          <button
            onClick={togglePlayPause}
            className="bg-primary-600 hover:bg-primary-700 text-white rounded-full p-4 transition-colors"
          >
            {isPlaying ? (
              <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zM7 8a1 1 0 012 0v4a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v4a1 1 0 102 0V8a1 1 0 00-1-1z"
                  clipRule="evenodd"
                />
              </svg>
            ) : (
              <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z"
                  clipRule="evenodd"
                />
              </svg>
            )}
          </button>

          <div className="flex-1">
            <input
              type="range"
              min="0"
              max={duration}
              value={currentTime}
              onChange={handleSeek}
              className="w-full"
            />
            <div className="flex justify-between text-sm text-gray-600 mt-1">
              <span>{formatTime(currentTime)}</span>
              <span>{formatTime(duration)}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Individual Track Controls */}
      <div className="space-y-4">
        {tracks.map((track) => {
          const state = trackStates.get(track.id);
          return (
            <div key={track.id} className="bg-white shadow-lg rounded-lg p-4">
              <div className="flex items-center justify-between mb-3">
                <h4 className="font-semibold text-gray-900 capitalize">
                  {track.instrument_name}
                </h4>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => toggleSolo(track.id)}
                    className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                      state?.solo
                        ? 'bg-yellow-500 text-white'
                        : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                    }`}
                  >
                    S
                  </button>
                  <button
                    onClick={() => toggleMute(track.id)}
                    className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                      state?.muted
                        ? 'bg-red-500 text-white'
                        : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                    }`}
                  >
                    M
                  </button>
                  <button
                    onClick={() => downloadTrack(track.id, track.instrument_name)}
                    className="px-3 py-1 rounded text-sm font-medium bg-primary-600 text-white hover:bg-primary-700 transition-colors"
                  >
                    Download
                  </button>
                </div>
              </div>

              <div
                ref={(el) => {
                  if (el) containerRefs.current.set(track.id, el);
                }}
                className="mb-3"
              />

              <div className="flex items-center space-x-3">
                <svg className="w-5 h-5 text-gray-500" fill="currentColor" viewBox="0 0 20 20">
                  <path
                    fillRule="evenodd"
                    d="M9.383 3.076A1 1 0 0110 4v12a1 1 0 01-1.707.707L4.586 13H2a1 1 0 01-1-1V8a1 1 0 011-1h2.586l3.707-3.707a1 1 0 011.09-.217zM14.657 2.929a1 1 0 011.414 0A9.972 9.972 0 0119 10a9.972 9.972 0 01-2.929 7.071 1 1 0 01-1.414-1.414A7.971 7.971 0 0017 10c0-2.21-.894-4.208-2.343-5.657a1 1 0 010-1.414zm-2.829 2.828a1 1 0 011.415 0A5.983 5.983 0 0115 10a5.984 5.984 0 01-1.757 4.243 1 1 0 01-1.415-1.415A3.984 3.984 0 0013 10a3.983 3.983 0 00-1.172-2.828 1 1 0 010-1.415z"
                    clipRule="evenodd"
                  />
                </svg>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={state?.volume || 80}
                  onChange={(e) => handleVolumeChange(track.id, parseInt(e.target.value))}
                  className="flex-1"
                />
                <span className="text-sm text-gray-600 w-12 text-right">
                  {state?.volume || 80}%
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default InstrumentPlayer;
