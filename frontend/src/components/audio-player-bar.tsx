"use client";

import React, { useRef, useState, useEffect } from "react";
import { Play, Pause, RotateCcw, RotateCw, Volume2 } from "lucide-react";

interface AudioPlayerBarProps {
  audioUrl?: string;
  currentTime: number;
  onTimeUpdate: (timeMs: number) => void;
  onSeek: (timeMs: number) => void;
}

export function AudioPlayerBar({ audioUrl, currentTime, onTimeUpdate, onSeek }: AudioPlayerBarProps) {
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [duration, setDuration] = useState(0);
  const [playbackRate, setPlaybackRate] = useState(1);

  const togglePlay = () => {
    if (!audioRef.current) return;
    if (isPlaying) {
      audioRef.current.pause();
    } else {
      audioRef.current.play();
    }
  };

  const handleTimeUpdate = () => {
    if (audioRef.current) {
      onTimeUpdate(Math.round(audioRef.current.currentTime * 1000));
    }
  };

  const handleLoadedMetadata = () => {
    if (audioRef.current) {
      setDuration(audioRef.current.duration);
    }
  };

  const handleSeekChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newTime = parseFloat(e.target.value);
    if (audioRef.current) {
      audioRef.current.currentTime = newTime;
    }
    onSeek(Math.round(newTime * 1000));
  };

  const skip = (seconds: number) => {
    if (audioRef.current) {
      audioRef.current.currentTime = Math.max(0, Math.min(audioRef.current.currentTime + seconds, duration));
    }
  };

  const changeRate = () => {
    const rates = [1, 1.25, 1.5, 1.75, 2];
    const nextRate = rates[(rates.indexOf(playbackRate) + 1) % rates.length];
    setPlaybackRate(nextRate);
    if (audioRef.current) {
      audioRef.current.playbackRate = nextRate;
    }
  };

  const formatTime = (secs: number) => {
    const m = Math.floor(secs / 60);
    const s = Math.floor(secs % 60);
    return `${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
  };

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 px-6 py-3 shadow-lg z-30">
      <audio
        ref={audioRef}
        src={audioUrl}
        onPlay={() => setIsPlaying(true)}
        onPause={() => setIsPlaying(false)}
        onTimeUpdate={handleTimeUpdate}
        onLoadedMetadata={handleLoadedMetadata}
      />

      <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center gap-4">
        {/* Controls */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => skip(-5)}
            className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-full"
            title="Lùi 5s"
          >
            <RotateCcw className="w-4 h-4" />
          </button>

          <button
            onClick={togglePlay}
            className="p-3 bg-blue-600 hover:bg-blue-700 text-white rounded-full shadow-md transition-colors"
          >
            {isPlaying ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5 ml-0.5" />}
          </button>

          <button
            onClick={() => skip(5)}
            className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-full"
            title="Tới 5s"
          >
            <RotateCw className="w-4 h-4" />
          </button>
        </div>

        {/* Scrubber */}
        <div className="flex-1 flex items-center gap-3 w-full">
          <span className="text-xs text-gray-500 font-mono w-12 text-right">
            {formatTime(currentTime / 1000)}
          </span>
          <input
            type="range"
            min={0}
            max={duration || 100}
            step={0.1}
            value={currentTime / 1000}
            onChange={handleSeekChange}
            className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
          />
          <span className="text-xs text-gray-500 font-mono w-12">
            {formatTime(duration)}
          </span>
        </div>

        {/* Speed */}
        <button
          onClick={changeRate}
          className="px-2.5 py-1 text-xs font-semibold bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-md transition-colors"
        >
          {playbackRate}x
        </button>
      </div>
    </div>
  );
}
