import React from 'react';
import {
  Popover,
  Box,
  Typography,
  Button,
  IconButton,
  Paper,
  Fade,
} from '@mui/material';
import { Cookie, Close, Chat, Info, Warning, Restaurant } from '@mui/icons-material';

interface MenuItemAIPopupProps {
  anchorEl: HTMLElement | null;
  open: boolean;
  onClose: () => void;
  menuItem: {
    id: string;
    name: string;
    description: string;
    price: number;
    allergen_info?: string[];
    is_signature?: boolean;
  };
  onAskAI: (question: string, menuItem: any) => void;
}

const MenuItemAIPopup: React.FC<MenuItemAIPopupProps> = ({
  anchorEl,
  open,
  onClose,
  menuItem,
  onAskAI,
}) => {
  const handleAskAboutItem = () => {
    const question = `Tell me more about the ${menuItem.name}. What makes it special?`;
    onAskAI(question, menuItem);
    onClose();
  };

  const handleAskAboutIngredients = () => {
    const question = `What are the main ingredients in the ${menuItem.name}?`;
    onAskAI(question, menuItem);
    onClose();
  };

  const handleAskAboutAllergens = () => {
    const question = `What allergens should I be aware of for the ${menuItem.name}?`;
    onAskAI(question, menuItem);
    onClose();
  };

  const handleCustomizations = () => {
    const question = `Can I customize the ${menuItem.name}? What options are available?`;
    onAskAI(question, menuItem);
    onClose();
  };

  const handlePairings = () => {
    const question = `What would you recommend to pair with the ${menuItem.name}?`;
    onAskAI(question, menuItem);
    onClose();
  };

  return (
    <Popover
      open={open}
      anchorEl={anchorEl}
      onClose={onClose}
      anchorOrigin={{
        vertical: 'top',
        horizontal: 'right',
      }}
      transformOrigin={{
        vertical: 'bottom',
        horizontal: 'left',
      }}
      TransitionComponent={Fade}
      sx={{
        '& .MuiPopover-paper': {
          backgroundImage: 'linear-gradient(135deg, #FFF8F3 0%, #FFEFD5 100%)',
          boxShadow: '0 12px 40px rgba(139, 69, 19, 0.15)',
          borderRadius: 3,
          border: '2px solid #D2691E',
          overflow: 'visible',
        },
      }}
      disableAutoFocus
      disableEnforceFocus
      disableRestoreFocus
    >
      <Paper 
        sx={{ 
          p: 2.5, 
          maxWidth: 320,
          backgroundColor: 'transparent',
          backgroundImage: 'none',
          boxShadow: 'none',
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Cookie 
            sx={{ 
              color: '#D2691E', 
              mr: 1.5,
              fontSize: '1.8rem'
            }} 
          />
          <Typography 
            variant="h6" 
            sx={{ 
              fontWeight: 700, 
              flex: 1,
              color: '#8B4513',
              fontSize: '1.2rem'
            }}
          >
            Ask Baker Betty
          </Typography>
          <IconButton 
            size="small" 
            onClick={onClose} 
            sx={{ 
              ml: 1,
              color: '#8B4513',
              '&:hover': {
                backgroundColor: 'rgba(139, 69, 19, 0.1)'
              }
            }}
          >
            <Close fontSize="small" />
          </IconButton>
        </Box>
        
        <Typography 
          variant="body2" 
          sx={{ 
            mb: 2.5,
            color: '#5D4037',
            backgroundColor: 'rgba(255, 255, 255, 0.8)',
            padding: '8px 12px',
            borderRadius: 2,
            textAlign: 'center'
          }}
        >
          What would you like to know about the <strong style={{ color: '#8B4513' }}>{menuItem.name}</strong>?
        </Typography>
        
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.2 }}>
          <Button
            variant="contained"
            size="small"
            startIcon={<Info />}
            onClick={handleAskAboutItem}
            sx={{ 
              justifyContent: 'flex-start', 
              textTransform: 'none',
              backgroundColor: '#D2691E',
              color: 'white',
              fontWeight: 600,
              '&:hover': {
                backgroundColor: '#B8600F'
              },
              boxShadow: '0 2px 8px rgba(139, 69, 19, 0.2)'
            }}
          >
            Tell me more about this cookie
          </Button>
          
          <Button
            variant="outlined"
            size="small"
            startIcon={<Restaurant />}
            onClick={handleAskAboutIngredients}
            sx={{ 
              justifyContent: 'flex-start', 
              textTransform: 'none',
              borderColor: '#D2691E',
              color: '#8B4513',
              fontWeight: 600,
              '&:hover': {
                borderColor: '#B8600F',
                backgroundColor: 'rgba(210, 105, 30, 0.05)'
              }
            }}
          >
            What are the ingredients?
          </Button>
          
          {menuItem.allergen_info && menuItem.allergen_info.length > 0 && (
            <Button
              variant="outlined"
              size="small"
              startIcon={<Warning />}
              onClick={handleAskAboutAllergens}
              sx={{ 
                justifyContent: 'flex-start', 
                textTransform: 'none',
                borderColor: '#FF6B6B',
                color: '#D73502',
                fontWeight: 600,
                '&:hover': {
                  borderColor: '#FF5252',
                  backgroundColor: 'rgba(255, 107, 107, 0.05)'
                }
              }}
            >
              Check allergen information
            </Button>
          )}

          <Button
            variant="outlined"
            size="small"
            startIcon={<Chat />}
            onClick={handleCustomizations}
            sx={{ 
              justifyContent: 'flex-start', 
              textTransform: 'none',
              borderColor: '#D2691E',
              color: '#8B4513',
              fontWeight: 600,
              '&:hover': {
                borderColor: '#B8600F',
                backgroundColor: 'rgba(210, 105, 30, 0.05)'
              }
            }}
          >
            Customization options
          </Button>

          <Button
            variant="outlined"
            size="small"
            startIcon={<Cookie />}
            onClick={handlePairings}
            sx={{ 
              justifyContent: 'flex-start', 
              textTransform: 'none',
              borderColor: '#D2691E',
              color: '#8B4513',
              fontWeight: 600,
              '&:hover': {
                borderColor: '#B8600F',
                backgroundColor: 'rgba(210, 105, 30, 0.05)'
              }
            }}
          >
            Pairing suggestions
          </Button>
        </Box>
      </Paper>
    </Popover>
  );
};

export default MenuItemAIPopup;