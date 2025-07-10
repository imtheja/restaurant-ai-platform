import React from 'react';
import {
  IconButton,
  Tooltip,
  Box
} from '@mui/material';
import {
  Mic,
  MicOff,
  VolumeUp,
  VolumeOff
} from '@mui/icons-material';

interface SpeechControlsProps {
  isListening: boolean;
  isSpeaking: boolean;
  onStartListening: () => void;
  onStopListening: () => void;
  onToggleSpeech: () => void;
  speechEnabled: boolean;
}

const SpeechControls: React.FC<SpeechControlsProps> = ({
  isListening,
  isSpeaking,
  onStartListening,
  onStopListening,
  onToggleSpeech,
  speechEnabled
}) => {
  return (
    <Box sx={{ display: 'flex', gap: 1 }}>
      {/* Speech toggle button */}
      <Tooltip title={speechEnabled ? "Disable speech" : "Enable speech"}>
        <IconButton 
          onClick={onToggleSpeech} 
          color={speechEnabled ? "primary" : "default"}
          sx={{
            transition: 'all 0.3s ease',
            '&:hover': {
              transform: 'scale(1.1)'
            }
          }}
        >
          {speechEnabled ? <VolumeUp /> : <VolumeOff />}
        </IconButton>
      </Tooltip>

      {/* Microphone button - only show if speech recognition is enabled */}
      {speechEnabled && (
        <Tooltip title={isListening ? "Stop listening" : "Start listening"}>
          <IconButton
            onClick={isListening ? onStopListening : onStartListening}
            disabled={isSpeaking}
            sx={{
              background: isListening 
                ? 'linear-gradient(135deg, #FF6B9D 0%, #FF8E53 100%)'
                : 'linear-gradient(135deg, #E0E0E0 0%, #BDBDBD 100%)',
              color: isListening ? 'white' : 'text.primary',
              border: '2px solid white',
              boxShadow: isListening 
                ? '0 4px 12px rgba(255, 107, 157, 0.4)'
                : '0 2px 6px rgba(0,0,0,0.1)',
              transition: 'all 0.3s ease',
              '&:hover': {
                transform: 'scale(1.1)',
                boxShadow: isListening 
                  ? '0 6px 16px rgba(255, 107, 157, 0.6)'
                  : '0 4px 12px rgba(0,0,0,0.2)',
              },
              '&:disabled': {
                opacity: 0.5,
                transform: 'none'
              }
            }}
          >
            {isListening ? <MicOff /> : <Mic />}
          </IconButton>
        </Tooltip>
      )}
    </Box>
  );
};

export default SpeechControls;