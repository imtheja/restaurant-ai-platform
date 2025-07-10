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
import DynamicChatInterface from './DynamicChatInterface';
import { useRestaurantTheme } from '@/hooks/useRestaurantTheme';

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
  const [sharedSessionId] = useState(() => `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`);
  const [visibleChatSendMessage, setVisibleChatSendMessage] = useState<((message: string, context?: any) => void) | null>(null);
  const [pendingMessage, setPendingMessage] = useState<{message: string, context?: any} | null>(null);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const restaurantTheme = useRestaurantTheme(restaurantSlug);
  

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

  // Send pending message when visible chat becomes ready
  React.useEffect(() => {
    if (visibleChatSendMessage && pendingMessage && open) {
      // Add a small delay to ensure the dialog is fully rendered
      setTimeout(() => {
        visibleChatSendMessage(pendingMessage.message, pendingMessage.context);
        setPendingMessage(null);
      }, 100);
    }
  }, [visibleChatSendMessage, pendingMessage, open]);

  return (
    <>
      {/* Hidden ChatInterface for onChatReady callback */}
      <Box sx={{ display: 'none' }}>
        <DynamicChatInterface
          restaurantSlug={restaurantSlug}
          onChatReady={(sendMessage) => {
            // Forward the sendMessage function to the parent
            if (onChatReady) {
              onChatReady((message: string, context?: any) => {
                // Always open the dialog first
                if (!open) {
                  handleOpen();
                }
                
                // Always set as pending message so it gets sent when visible chat is ready
                setPendingMessage({ message, context });
              });
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
          background: restaurantTheme.gradients.fab,
          boxShadow: `0 8px 32px ${restaurantTheme.primary}50`,
          border: '4px solid white',
          '&:hover': {
            transform: 'scale(1.1)',
            boxShadow: `0 12px 40px ${restaurantTheme.primary}66`,
            background: restaurantTheme.gradients.fab,
            filter: 'brightness(1.1)',
          },
          transition: 'all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275)',
          animation: 'pulse 2s ease-in-out infinite',
          '@keyframes pulse': {
            '0%': {
              boxShadow: `0 8px 32px ${restaurantTheme.primary}66`,
            },
            '50%': {
              boxShadow: `0 12px 40px ${restaurantTheme.primary}80`,
            },
            '100%': {
              boxShadow: `0 8px 32px ${restaurantTheme.primary}66`,
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
            background: restaurantTheme.gradients.header,
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
              <SmartToy sx={{ fontSize: 30, color: restaurantTheme.primary }} />
            </Box>
            <Box>
              <Typography variant="h5" sx={{ fontWeight: 700, textShadow: '1px 1px 2px rgba(0,0,0,0.3)' }}>
                🍪 Cookie Expert Betty
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
            <DynamicChatInterface
              restaurantSlug={restaurantSlug}
              onChatReady={(sendMessage) => {
                setVisibleChatSendMessage(() => sendMessage);
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