import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  Box,
  Typography,
  Avatar,
  CircularProgress,
  Alert,
  TextField,
  IconButton,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Paper
} from '@mui/material';
import { SmartToy, Send, Person } from '@mui/icons-material';
import { useQuery } from 'react-query';
import toast from 'react-hot-toast';

// Services
import { restaurantApi, chatApi } from '@services/api';
import { aiConfigApi, AIConfig } from '@services/aiConfigApi';
import { useRestaurantTheme } from '@/hooks/useRestaurantTheme';

// Types
import { ChatMessage } from '../../types';

interface DynamicChatInterfaceProps {
  restaurantSlug: string;
  onChatReady?: (sendMessage: (message: string, context?: any) => void) => void;
  isEmbedded?: boolean;
}

const DynamicChatInterface: React.FC<DynamicChatInterfaceProps> = ({ 
  restaurantSlug, 
  onChatReady, 
  isEmbedded = false 
}) => {
  // Core state
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [sessionId] = useState(() => `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`);
  const [isStreamingResponse, setIsStreamingResponse] = useState(false);
  const restaurantTheme = useRestaurantTheme(restaurantSlug);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Get AI configuration for this restaurant
  const { 
    data: aiConfig, 
    isLoading: configLoading, 
    error: configError 
  } = useQuery(
    ['aiConfig', restaurantSlug],
    () => aiConfigApi.getAIConfig(restaurantSlug),
    {
      staleTime: 5 * 60 * 1000, // Cache for 5 minutes
      retry: 3
    }
  );

  // Get restaurant/avatar config
  const { data: avatarConfig } = useQuery(
    ['avatarConfig', restaurantSlug],
    () => restaurantApi.getAvatarConfig(restaurantSlug),
    {
      staleTime: 10 * 60 * 1000
    }
  );

  // Auto-scroll to bottom
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  // Send message function
  const sendMessage = useCallback(async (messageText?: string, context?: any) => {
    const textToSend = messageText || inputMessage.trim();
    if (!textToSend || isStreamingResponse) return;


    const newUserMessage: ChatMessage = {
      id: `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      conversation_id: sessionId,
      sender_type: 'customer',
      content: textToSend,
      message_type: 'text',
      metadata: {},
      created_at: new Date().toISOString()
    };

    setMessages(prev => [...prev, newUserMessage]);
    
    // Create AI message placeholder
    const aiMessage: ChatMessage = {
      id: `ai-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      conversation_id: sessionId,
      sender_type: 'ai',
      content: '',
      message_type: 'text',
      metadata: {},
      created_at: new Date().toISOString()
    };

    setMessages(prev => [...prev, aiMessage]);
    setIsStreamingResponse(true);

    try {
      await chatApi.sendMessageStream(
        restaurantSlug,
        {
          message: textToSend,
          session_id: sessionId,
          context: context || { source: 'dynamic_chat' }
        },
        // onChunk - update message content as it streams
        (chunk: string) => {
          setMessages(prev => prev.map(msg => 
            msg.id === aiMessage.id 
              ? { ...msg, content: msg.content + chunk }
              : msg
          ));
        },
        // onComplete
        () => {
          setIsStreamingResponse(false);
        },
        // onError
        (error: string) => {
          setIsStreamingResponse(false);
          toast.error(error || 'Failed to get AI response');
          // Remove the failed AI message
          setMessages(prev => prev.filter(msg => msg.id !== aiMessage.id));
        }
      );
    } catch (error) {
      console.error('DynamicChatInterface: Error sending message:', error);
      setIsStreamingResponse(false);
      const errorMessage = error instanceof Error ? error.message : 'Failed to send message';
      toast.error(errorMessage);
      
      // Remove failed AI message
      setMessages(prev => prev.filter(msg => msg.id !== aiMessage.id));
    }
    
    if (!messageText) setInputMessage(''); // Only clear input if it was typed
  }, [inputMessage, sessionId, restaurantSlug, isStreamingResponse]);

  // Expose sendMessage function to parent
  useEffect(() => {
    if (onChatReady && sessionId) {
      onChatReady(sendMessage);
    }
  }, [onChatReady, sessionId, sendMessage]);

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  };

  // Loading state
  if (configLoading) {
    return (
      <Box sx={{ 
        height: isEmbedded ? '100%' : '70vh', 
        display: 'flex', 
        flexDirection: 'column',
        background: `linear-gradient(135deg, ${restaurantTheme.background} 0%, ${restaurantTheme.accent}40 50%, ${restaurantTheme.secondary}20 100%)`,
        justifyContent: 'center',
        alignItems: 'center'
      }}>
        <CircularProgress sx={{ mb: 2 }} />
        <Typography>Loading AI assistant...</Typography>
      </Box>
    );
  }

  // Error state
  if (configError) {
    return (
      <Box sx={{ 
        height: isEmbedded ? '100%' : '70vh', 
        display: 'flex', 
        flexDirection: 'column',
        background: `linear-gradient(135deg, ${restaurantTheme.background} 0%, ${restaurantTheme.accent}40 50%, ${restaurantTheme.secondary}20 100%)`,
        p: 2
      }}>
        <Alert severity="error">
          Failed to load AI configuration. Please try again later.
        </Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ 
      height: isEmbedded ? '100%' : '70vh', 
      display: 'flex', 
      flexDirection: 'column',
      background: `linear-gradient(135deg, ${restaurantTheme.background} 0%, ${restaurantTheme.accent}40 50%, ${restaurantTheme.secondary}20 100%)`
    }}>
      {/* Header */}
      {!isEmbedded && (
        <Box sx={{ 
          p: 2, 
          borderBottom: 1, 
          borderColor: 'divider',
          background: 'rgba(255,255,255,0.9)',
          backdropFilter: 'blur(10px)',
          display: 'flex',
          alignItems: 'center',
          gap: 2
        }}>
          <Avatar sx={{ bgcolor: restaurantTheme.primary }}>
            <SmartToy />
          </Avatar>
          <Box sx={{ flex: 1 }}>
            <Typography variant="h6">
              {(avatarConfig as any)?.name || 'Cookie Expert Betty'}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {aiConfig?.mode === 'text_only' 
                ? 'Text-only mode • Ask me anything about the menu!'
                : aiConfig?.mode === 'speech_enabled'
                ? 'Voice-enabled chat • Click to talk or type'
                : 'Hybrid mode • Speech optional'
              }
            </Typography>
          </Box>
        </Box>
      )}

      {/* Messages Area */}
      <Box sx={{ 
        flex: 1, 
        overflow: 'auto', 
        p: isEmbedded ? 1 : 2,
        display: 'flex',
        flexDirection: 'column'
      }}>
        {messages.length === 0 && (
          <Box sx={{ 
            display: 'flex', 
            flexDirection: 'column', 
            alignItems: 'center', 
            justifyContent: 'center', 
            flex: 1,
            textAlign: 'center',
            opacity: 0.7
          }}>
            <SmartToy sx={{ fontSize: 64, color: restaurantTheme.primary, mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              Hi! I'm {(avatarConfig as any)?.name || 'Cookie Expert Betty'}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Ask me about menu items, ingredients, allergens, or anything else!
            </Typography>
          </Box>
        )}

        {/* Message list */}
        <List sx={{ flex: 1, overflow: 'auto' }}>
          {messages.map((message, index) => (
            <ListItem 
              key={message.id || index}
              sx={{ 
                justifyContent: message.sender_type === 'customer' ? 'flex-end' : 'flex-start',
                mb: 1
              }}
            >
              <Paper 
                elevation={1}
                sx={{ 
                  p: 2, 
                  maxWidth: '70%',
                  backgroundColor: message.sender_type === 'customer' 
                    ? restaurantTheme.primary 
                    : 'background.paper',
                  borderRadius: 2
                }}
              >
                <Box sx={{ display: 'flex', gap: 1, alignItems: 'flex-start' }}>
                  <ListItemAvatar sx={{ minWidth: 40 }}>
                    <Avatar sx={{ 
                      bgcolor: message.sender_type === 'customer' ? 'white' : restaurantTheme.accent,
                      width: 32,
                      height: 32
                    }}>
                      {message.sender_type === 'customer' ? 
                        <Person sx={{ color: restaurantTheme.primary }} /> : 
                        <SmartToy sx={{ color: restaurantTheme.primary }} />
                      }
                    </Avatar>
                  </ListItemAvatar>
                  <ListItemText 
                    primary={message.content}
                    sx={{ 
                      '& .MuiTypography-root': { 
                        color: message.sender_type === 'customer' ? 'white' : 'text.primary' 
                      }
                    }}
                  />
                </Box>
              </Paper>
            </ListItem>
          ))}
          {isStreamingResponse && (
            <ListItem sx={{ justifyContent: 'flex-start' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <CircularProgress size={16} />
                <Typography variant="body2" color="text.secondary">
                  {(avatarConfig as any)?.name || 'Betty'} is typing...
                </Typography>
              </Box>
            </ListItem>
          )}
        </List>
        
        <div ref={messagesEndRef} />
      </Box>

      {/* Input Area */}
      <Box sx={{ 
        p: 2, 
        borderTop: 1, 
        borderColor: 'divider',
        background: 'rgba(255,255,255,0.9)',
        backdropFilter: 'blur(10px)'
      }}>
        <Box sx={{ display: 'flex', gap: 1, alignItems: 'flex-end' }}>
          <TextField
            fullWidth
            multiline
            maxRows={3}
            placeholder="Ask me anything about our cookies..."
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={isStreamingResponse}
            variant="outlined"
            size="small"
            sx={{
              '& .MuiOutlinedInput-root': {
                borderRadius: '16px',
                background: 'white',
                '&:hover': {
                  '& fieldset': {
                    borderColor: restaurantTheme.primary,
                  }
                },
                '&.Mui-focused': {
                  '& fieldset': {
                    borderColor: restaurantTheme.primary,
                  }
                }
              }
            }}
          />
          <IconButton
            onClick={() => sendMessage()}
            disabled={!inputMessage.trim() || isStreamingResponse}
            sx={{
              width: 48,
              height: 48,
              borderRadius: '12px',
              background: restaurantTheme.gradients.button,
              color: 'white',
              '&:hover': { 
                background: `linear-gradient(135deg, ${restaurantTheme.secondary} 0%, ${restaurantTheme.primary} 100%)`,
              },
              '&:disabled': {
                background: '#E0E0E0',
                color: '#999'
              }
            }}
          >
            <Send />
          </IconButton>
        </Box>
        
        <Typography variant="caption" color="text.secondary" sx={{ display: 'block', textAlign: 'center', mt: 1 }}>
          Mode: {aiConfig?.mode || 'text_only'}
        </Typography>
      </Box>
    </Box>
  );
};

export default DynamicChatInterface;