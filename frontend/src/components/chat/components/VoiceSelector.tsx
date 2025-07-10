import React, { useState } from 'react';
import {
  IconButton,
  Menu,
  MenuItem,
  Typography,
  Box,
  Tooltip
} from '@mui/material';
import { Settings } from '@mui/icons-material';

interface Voice {
  id: string;
  name: string;
  description: string;
  gender: string;
  recommended_for: string;
}

interface VoiceSelectorProps {
  voices: Voice[];
  selectedVoice: string;
  onVoiceSelect: (voiceId: string) => void;
}

const VoiceSelector: React.FC<VoiceSelectorProps> = ({
  voices,
  selectedVoice,
  onVoiceSelect
}) => {
  const [anchorEl, setAnchorEl] = useState<HTMLElement | null>(null);
  const open = Boolean(anchorEl);

  const handleClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleVoiceSelect = (voiceId: string) => {
    onVoiceSelect(voiceId);
    handleClose();
  };

  const selectedVoiceData = voices.find(voice => voice.id === selectedVoice);

  return (
    <>
      <Tooltip title="Select voice">
        <IconButton 
          onClick={handleClick}
          color="primary"
          sx={{
            transition: 'all 0.3s ease',
            '&:hover': {
              transform: 'scale(1.1)'
            }
          }}
        >
          <Settings />
        </IconButton>
      </Tooltip>
      
      <Menu
        anchorEl={anchorEl}
        open={open}
        onClose={handleClose}
        PaperProps={{
          sx: {
            background: 'linear-gradient(135deg, #FFFFFF 0%, #FFF8DC 100%)',
            border: '2px solid #FFD93D',
            borderRadius: '12px',
            mt: 1,
            minWidth: 280
          }
        }}
      >
        {voices.map((voice) => (
          <MenuItem
            key={voice.id}
            selected={voice.id === selectedVoice}
            onClick={() => handleVoiceSelect(voice.id)}
            sx={{
              background: voice.id === selectedVoice 
                ? 'linear-gradient(135deg, #FFD93D 0%, #FF8E53 50%)' 
                : 'transparent',
              color: voice.id === selectedVoice ? 'white' : '#5D4037',
              fontWeight: voice.id === selectedVoice ? 600 : 400,
              borderRadius: '8px',
              mx: 1,
              my: 0.5,
              '&:hover': {
                background: voice.id === selectedVoice 
                  ? 'linear-gradient(135deg, #FFD93D 0%, #FF8E53 50%)' 
                  : 'linear-gradient(135deg, #FFF8DC 0%, #FFD93D 20%)',
              }
            }}
          >
            <Box>
              <Typography variant="body2" fontWeight={600}>
                {voice.name}
                {voice.id === selectedVoice && ' ✓'}
              </Typography>
              <Typography 
                variant="caption" 
                color={voice.id === selectedVoice ? 'rgba(255,255,255,0.8)' : 'text.secondary'}
                sx={{ display: 'block' }}
              >
                {voice.description}
              </Typography>
              <Typography 
                variant="caption" 
                color={voice.id === selectedVoice ? 'rgba(255,255,255,0.7)' : 'text.secondary'}
                sx={{ fontSize: '10px' }}
              >
                Best for: {voice.recommended_for.replace(/_/g, ' ')}
              </Typography>
            </Box>
          </MenuItem>
        ))}
      </Menu>
    </>
  );
};

export default VoiceSelector;