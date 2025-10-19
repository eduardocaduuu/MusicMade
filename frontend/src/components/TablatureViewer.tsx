import React, { useState } from 'react';
import { Track, InstrumentType, TablatureCreate, Tablature } from '../types';
import { apiClient } from '../services/api';

interface TablatureViewerProps {
  track: Track;
}

const TablatureViewer: React.FC<TablatureViewerProps> = ({ track }) => {
  const [generating, setGenerating] = useState(false);
  const [tablature, setTablature] = useState<Tablature | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [selectedInstrument, setSelectedInstrument] = useState<InstrumentType>(
    InstrumentType.GUITAR
  );
  const [tuning, setTuning] = useState('standard');

  const handleGenerate = async () => {
    setGenerating(true);
    setError(null);

    try {
      const params: TablatureCreate = {
        instrument_type: selectedInstrument,
        tuning,
      };

      const tab = await apiClient.generateTablature(track.id, params);
      setTablature(tab);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to generate tablature');
    } finally {
      setGenerating(false);
    }
  };

  const downloadTablature = () => {
    if (!tablature) return;

    const blob = new Blob([tablature.content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${track.instrument_name}_tablature.txt`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="bg-white shadow-lg rounded-lg p-6 space-y-6">
      <h3 className="text-xl font-semibold text-gray-900">
        Tablature Generator - {track.instrument_name}
      </h3>

      {!tablature ? (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Instrument Type
            </label>
            <select
              value={selectedInstrument}
              onChange={(e) => setSelectedInstrument(e.target.value as InstrumentType)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value={InstrumentType.GUITAR}>Guitar</option>
              <option value={InstrumentType.BASS}>Bass</option>
              <option value={InstrumentType.PIANO}>Piano</option>
            </select>
          </div>

          {(selectedInstrument === InstrumentType.GUITAR ||
            selectedInstrument === InstrumentType.BASS) && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Tuning</label>
              <select
                value={tuning}
                onChange={(e) => setTuning(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="standard">Standard</option>
                {selectedInstrument === InstrumentType.GUITAR && (
                  <>
                    <option value="drop_d">Drop D</option>
                    <option value="half_step_down">Half Step Down</option>
                  </>
                )}
                {selectedInstrument === InstrumentType.BASS && (
                  <option value="5_string">5 String</option>
                )}
              </select>
            </div>
          )}

          <button
            onClick={handleGenerate}
            disabled={generating}
            className="w-full px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-md font-medium disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {generating ? (
              <span className="flex items-center justify-center">
                <svg
                  className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  ></circle>
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  ></path>
                </svg>
                Generating...
              </span>
            ) : (
              'Generate Tablature'
            )}
          </button>

          {error && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-md">
              <p className="text-sm text-red-600">{error}</p>
            </div>
          )}
        </div>
      ) : (
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <div>
              <p className="text-sm text-gray-600">
                Instrument: <span className="font-medium">{tablature.instrument_type}</span>
              </p>
              <p className="text-sm text-gray-600">
                Tuning: <span className="font-medium">{tablature.tuning}</span>
              </p>
            </div>
            <div className="space-x-2">
              <button
                onClick={downloadTablature}
                className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-md font-medium transition-colors"
              >
                Download
              </button>
              <button
                onClick={() => setTablature(null)}
                className="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-md font-medium transition-colors"
              >
                Generate New
              </button>
            </div>
          </div>

          <div className="bg-gray-50 border border-gray-300 rounded-md p-4 overflow-x-auto">
            <pre className="text-xs font-mono whitespace-pre">{tablature.content}</pre>
          </div>
        </div>
      )}
    </div>
  );
};

export default TablatureViewer;
