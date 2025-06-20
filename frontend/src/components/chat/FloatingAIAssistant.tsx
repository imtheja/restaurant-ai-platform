import React, { useState } from 'react';
import {
  Fab,
  Dialog,
  DialogTitle,
  DialogContent,
  IconButton,
  Box,
  Typography,
  Slide,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import { SmartToy, Close } from '@mui/icons-material';
import { TransitionProps } from '@mui/material/transitions';
import ChatInterface from './ChatInterface';

const Transition = React.forwardRef(function Transition(
  props: TransitionProps & {
    children: React.ReactElement<any, any>;
  },
  ref: React.Ref<unknown>,
) {
  return <Slide direction="up" ref={ref} {...props} />;
});

interface FloatingAIAssistantProps {
  restaurantSlug: string;
  onChatReady?: (sendMessage: (message: string, context?: any) => void) => void;
  shouldAutoOpen?: boolean;
  onOpenChange?: (isOpen: boolean) => void;
}

const FloatingAIAssistant: React.FC<FloatingAIAssistantProps> = ({
  restaurantSlug,
  onChatReady,
  shouldAutoOpen = false,
  onOpenChange,
}) => {
  const [open, setOpen] = useState(false);
  const [hasInitialized, setHasInitialized] = useState(false);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const handleOpen = () => {
    setOpen(true);
    onOpenChange?.(true);
  };
  
  const handleClose = () => {
    setOpen(false);
    onOpenChange?.(false);
  };

  // Auto-open when shouldAutoOpen changes to true
  React.useEffect(() => {
    if (shouldAutoOpen && !open) {
      handleOpen();
    }
  }, [shouldAutoOpen, open]);

  // Initialize chat early
  React.useEffect(() => {
    if (!hasInitialized) {
      setHasInitialized(true);
    }
  }, [hasInitialized]);

  return (
    <>
      {/* Hidden ChatInterface for early initialization */}
      <Box sx={{ display: 'none' }}>
        <ChatInterface
          restaurantSlug={restaurantSlug}
          onChatReady={(sendMessage) => {
            console.log('FloatingAIAssistant: ChatInterface is ready, forwarding to parent');
            if (onChatReady) {
              onChatReady(sendMessage);
            } else {
              console.log('FloatingAIAssistant: No onChatReady callback from parent');
            }
          }}
          isEmbedded={true}
        />
      </Box>

      {/* Floating Action Button */}
      <Fab
        onClick={handleOpen}
        sx={{
          position: 'fixed',
          bottom: 24,
          right: 24,
          zIndex: 1000,
          width: 80,
          height: 80,
          background: 'linear-gradient(135deg, #FF6B9D 0%, #FF8E53 50%, #FFD93D 100%)',
          boxShadow: '0 8px 32px rgba(255, 107, 157, 0.4)',
          border: '4px solid white',
          '&:hover': {
            transform: 'scale(1.15) rotate(5deg)',
            boxShadow: '0 16px 48px rgba(255, 107, 157, 0.6)',
            background: 'linear-gradient(135deg, #FF8E53 0%, #FFD93D 50%, #FF6B9D 100%)',
          },
          transition: 'all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275)',
          animation: 'pulse 2s ease-in-out infinite',
          '@keyframes pulse': {
            '0%': {
              boxShadow: '0 8px 32px rgba(255, 107, 157, 0.4)',
            },
            '50%': {
              boxShadow: '0 12px 40px rgba(255, 107, 157, 0.6)',
            },
            '100%': {
              boxShadow: '0 8px 32px rgba(255, 107, 157, 0.4)',
            }
          }
        }}
      >
        <SmartToy sx={{ fontSize: 40, color: 'white', filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.3))' }} />
      </Fab>

      {/* Chat Dialog */}
      <Dialog
        open={open}
        onClose={handleClose}
        TransitionComponent={Transition}
        maxWidth="md"
        fullWidth
        fullScreen={isMobile}
        PaperProps={{
          sx: {
            height: isMobile ? '100%' : '80vh',
            maxHeight: isMobile ? '100%' : '80vh',
            borderRadius: isMobile ? 0 : 2,
            overflow: 'hidden',
          },
        }}
      >
        <DialogTitle
          sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            background: 'linear-gradient(135deg, #FF6B9D 0%, #FF8E53 50%, #FFD93D 100%)',
            color: 'white',
            py: 3,
            position: 'relative',
            overflow: 'hidden',
            '&::before': {
              content: '""',
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              background: 'url("data:image/svg+xml,%3Csvg width="60" height="60" viewBox="0 0 60 60" xmlns="http://www.w3.org/2000/svg"%3E%3Cg fill="none" fill-rule="evenodd"%3E%3Cg fill="%23ffffff" fill-opacity="0.1"%3E%3Ccircle cx="7" cy="7" r="3"/%3E%3Ccircle cx="27" cy="7" r="3"/%3E%3Ccircle cx="47" cy="7" r="3"/%3E%3Ccircle cx="7" cy="27" r="3"/%3E%3Ccircle cx="27" cy="27" r="3"/%3E%3Ccircle cx="47" cy="27" r="3"/%3E%3Ccircle cx="7" cy="47" r="3"/%3E%3Ccircle cx="27" cy="47" r="3"/%3E%3Ccircle cx="47" cy="47" r="3"/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")',
              pointerEvents: 'none'
            }
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, position: 'relative', zIndex: 1 }}>
            <Box
              sx={{
                width: 50,
                height: 50,
                borderRadius: '50%',
                background: 'rgba(255,255,255,0.9)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: '0 4px 12px rgba(0,0,0,0.2)'
              }}
            >
              <SmartToy sx={{ fontSize: 30, color: '#FF6B9D' }} />
            </Box>
            <Box>
              <Typography variant="h5" sx={{ fontWeight: 700, textShadow: '1px 1px 2px rgba(0,0,0,0.3)' }}>
                🍪 Baker Betty
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.9, textShadow: '1px 1px 2px rgba(0,0,0,0.3)' }}>
                Your Cookie Expert!
              </Typography>
            </Box>
          </Box>
          <IconButton
            onClick={handleClose}
            sx={{ 
              color: 'white',
              bgcolor: 'rgba(255,255,255,0.2)',
              '&:hover': { bgcolor: 'rgba(255,255,255,0.3)' },
              position: 'relative',
              zIndex: 1
            }}
          >
            <Close />
          </IconButton>
        </DialogTitle>
        
        <DialogContent sx={{ p: 0, height: '100%', overflow: 'hidden' }}>
          <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            <ChatInterface
              restaurantSlug={restaurantSlug}
              onChatReady={() => {
                // This instance is just for display, the hidden one handles the callback
              }}
              isEmbedded={true}
            />
          </Box>
        </DialogContent>
      </Dialog>
    </>
  );
};

export default FloatingAIAssistant;