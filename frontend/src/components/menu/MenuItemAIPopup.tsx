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
import { SmartToy, Close, Chat } from '@mui/icons-material';

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
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.12)',
          borderRadius: 2,
          border: '1px solid rgba(0, 0, 0, 0.05)',
        },
      }}
      disableAutoFocus
      disableEnforceFocus
      disableRestoreFocus
    >
      <Paper sx={{ p: 2, maxWidth: 280 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1.5 }}>
          <SmartToy sx={{ color: 'primary.main', mr: 1 }} />
          <Typography variant="subtitle2" sx={{ fontWeight: 600, flex: 1 }}>
            Ask Baker Betty
          </Typography>
          <IconButton size="small" onClick={onClose} sx={{ ml: 1 }}>
            <Close fontSize="small" />
          </IconButton>
        </Box>
        
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          What would you like to know about <strong>{menuItem.name}</strong>?
        </Typography>
        
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
          <Button
            variant="outlined"
            size="small"
            startIcon={<Chat />}
            onClick={handleAskAboutItem}
            sx={{ justifyContent: 'flex-start', textTransform: 'none' }}
          >
            Tell me more about this item
          </Button>
          
          <Button
            variant="outlined"
            size="small"
            startIcon={<Chat />}
            onClick={handleAskAboutIngredients}
            sx={{ justifyContent: 'flex-start', textTransform: 'none' }}
          >
            What are the ingredients?
          </Button>
          
          {menuItem.allergen_info && menuItem.allergen_info.length > 0 && (
            <Button
              variant="outlined"
              size="small"
              startIcon={<Chat />}
              onClick={handleAskAboutAllergens}
              sx={{ justifyContent: 'flex-start', textTransform: 'none' }}
            >
              Check allergen information
            </Button>
          )}
        </Box>
      </Paper>
    </Popover>
  );
};

export default MenuItemAIPopup;