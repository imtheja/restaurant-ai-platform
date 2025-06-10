import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Typography,
  Container,
  Paper,
  IconButton,
  TextField,
  Button,
  List,
  ListItem,
  ListItemText,
  Avatar,
  Chip,
  CircularProgress,
  Fab,
  Tooltip
} from '@mui/material';
import {
  Mic,
  MicOff,
  Send,
  VolumeUp,
  VolumeOff,
  Person,
  SmartToy
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { useQuery, useMutation } from 'react-query';
import toast from 'react-hot-toast';

// Services
import { chatApi, restaurantApi } from '@services/api';

// Types
import { ChatMessage } from '@types/index';

interface ChatInterfaceProps {
  restaurantSlug: string;
  onChatReady?: (sendMessage: (message: string) => void) => void;
  isEmbedded?: boolean;
}

interface SpeechRecognitionEvent extends Event {
  results: {
    [index: number]: {
      [index: number]: {
        transcript: string;
        confidence: number;
      };
      isFinal: boolean;
    };
  };
  resultIndex: number;
}

interface SpeechRecognition extends EventTarget {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  start(): void;
  stop(): void;
  onresult: (event: SpeechRecognitionEvent) => void;
  onerror: (event: Event) => void;
  onend: () => void;
}

declare global {
  interface Window {
    SpeechRecognition: new () => SpeechRecognition;
    webkitSpeechRecognition: new () => SpeechRecognition;
  }
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ restaurantSlug, onChatReady, isEmbedded = false }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [speechEnabled, setSpeechEnabled] = useState(true);
  const [sessionId] = useState(() => `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`);
  const [speechTranscript, setSpeechTranscript] = useState('');
  const [isProcessingSpeech, setIsProcessingSpeech] = useState(false);
  
  const recognitionRef = useRef<SpeechRecognition | null>(null);
  const synthRef = useRef<SpeechSynthesis | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const speechTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Get avatar configuration
  const { data: avatarConfig } = useQuery(
    ['avatar', restaurantSlug],
    () => restaurantApi.getAvatarConfig(restaurantSlug),
    {
      enabled: !!restaurantSlug,
    }
  );

  // Send message mutation
  const sendMessageMutation = useMutation(
    (message: string) => chatApi.sendMessage(restaurantSlug, {
      message,
      session_id: sessionId,
      context: { source: 'voice_chat' }
    }),
    {
      onSuccess: (response) => {
        const aiMessage: ChatMessage = {
          id: response.message_id,
          conversation_id: response.conversation_id,
          sender_type: 'ai',
          content: response.message,
          message_type: 'text',
          created_at: new Date().toISOString()
        };
        setMessages(prev => [...prev, aiMessage]);

        // Speak the AI response if speech is enabled
        if (speechEnabled && response.message) {
          speakText(response.message);
        }
      },
      onError: (error: Error) => {
        toast.error(error.message || 'Failed to send message');
      }
    }
  );

  // Initialize speech recognition
  useEffect(() => {
    if (typeof window !== 'undefined') {
      synthRef.current = window.speechSynthesis;
      
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (SpeechRecognition) {
        recognitionRef.current = new SpeechRecognition();
        const recognition = recognitionRef.current;
        
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = 'en-US';

        recognition.onresult = (event: SpeechRecognitionEvent) => {
          let transcript = '';
          let isFinal = false;
          
          for (let i = event.resultIndex; i < event.results.length; i++) {
            const result = event.results[i];
            transcript += result[0].transcript;
            if (result.isFinal) {
              isFinal = true;
            }
          }
          
          // Auto-correct and format transcript
          const correctedTranscript = autoCorrectSpeech(transcript.trim());
          setSpeechTranscript(correctedTranscript);
          setInputMessage(correctedTranscript);
          
          if (isFinal && correctedTranscript.length > 0) {
            // Clear any existing timeout
            if (speechTimeoutRef.current) {
              clearTimeout(speechTimeoutRef.current);
            }
            
            // Auto-send after a short delay
            speechTimeoutRef.current = setTimeout(() => {
              setIsProcessingSpeech(true);
              sendMessage(correctedTranscript);
              setSpeechTranscript('');
              setIsProcessingSpeech(false);
              stopListening();
            }, 500);
          }
        };

        recognition.onerror = (event) => {
          console.error('Speech recognition error:', event);
          setIsListening(false);
          toast.error('Speech recognition error. Please try again.');
        };

        recognition.onend = () => {
          setIsListening(false);
        };
      } else {
        toast.error('Speech recognition not supported in this browser');
      }
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      if (synthRef.current) {
        synthRef.current.cancel();
      }
      if (speechTimeoutRef.current) {
        clearTimeout(speechTimeoutRef.current);
      }
    };
  }, []);

  // Scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Add welcome message when avatar config loads
  useEffect(() => {
    if (avatarConfig && messages.length === 0) {
      const welcomeMessage: ChatMessage = {
        id: `welcome-${Date.now()}`,
        conversation_id: sessionId,
        sender_type: 'ai',
        content: avatarConfig.greeting || "Hello! How can I help you today?",
        message_type: 'text',
        created_at: new Date().toISOString()
      };
      setMessages([welcomeMessage]);

      // Speak welcome message
      if (speechEnabled && avatarConfig.greeting) {
        setTimeout(() => speakText(avatarConfig.greeting), 500);
      }
    }
  }, [avatarConfig, speechEnabled, sessionId, messages.length]);

  // Expose sendMessage function to parent
  useEffect(() => {
    if (onChatReady) {
      onChatReady(sendMessage);
    }
  }, [onChatReady]);

  const speakText = (text: string) => {
    if (!synthRef.current || !speechEnabled) return;

    // Cancel any ongoing speech
    synthRef.current.cancel();

    // Remove emojis and clean text for speech
    const cleanText = text
      .replace(/[\u{1F600}-\u{1F64F}]|[\u{1F300}-\u{1F5FF}]|[\u{1F680}-\u{1F6FF}]|[\u{1F1E0}-\u{1F1FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]/gu, '') // Remove emojis
      .replace(/\s+/g, ' ') // Clean up extra spaces
      .trim();

    if (!cleanText) return;

    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.rate = 1.0; // Normal speed, not anxious
    utterance.pitch = 1.0; // Normal pitch
    utterance.volume = 0.8;

    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => setIsSpeaking(false);

    synthRef.current.speak(utterance);
  };

  const startListening = () => {
    if (!recognitionRef.current) {
      toast.error('Speech recognition not available');
      return;
    }

    try {
      setInputMessage('');
      setIsListening(true);
      recognitionRef.current.start();
    } catch (error) {
      console.error('Error starting speech recognition:', error);
      setIsListening(false);
      toast.error('Failed to start listening');
    }
  };

  const stopListening = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
    setIsListening(false);
  };

  const toggleSpeech = () => {
    setSpeechEnabled(!speechEnabled);
    if (speechEnabled && synthRef.current) {
      synthRef.current.cancel();
      setIsSpeaking(false);
    }
  };

  const sendMessage = (message?: string) => {
    const messageToSend = message || inputMessage.trim();
    if (!messageToSend) return;

    // Add user message
    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      conversation_id: sessionId,
      sender_type: 'customer',
      content: messageToSend,
      message_type: 'text',
      created_at: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    
    // Send to AI
    sendMessageMutation.mutate(messageToSend);
    if (!message) setInputMessage(''); // Only clear input if it was typed
  };

  const autoCorrectSpeech = (text: string): string => {
    if (!text) return text;
    
    // Basic auto-corrections for common speech recognition errors
    const corrections: { [key: string]: string } = {
      // Common food-related corrections
      'cookie jar': 'Cookie Jar',
      'baker betty': 'Baker Betty',
      'semi sweet': 'Semi Sweet',
      'cocoa': 'Cocoa',
      'biscoff': 'Biscoff',
      'oreo': 'Oreo',
      'tres leches': 'Tres Leches',
      'pistachio': 'Pistachio',
      'dubai chocolate': 'Dubai Chocolate',
      'cream cheese': 'Cream Cheese',
      // Common phrases
      'tell me about': 'Tell me about',
      'what is': 'What is',
      'whats': "What's",
      'id like': "I'd like",
      'i want': 'I want',
      'can you': 'Can you',
      'do you have': 'Do you have',
    };
    
    let corrected = text.toLowerCase();
    
    // Apply corrections
    Object.entries(corrections).forEach(([wrong, right]) => {
      const regex = new RegExp(`\\b${wrong}\\b`, 'gi');
      corrected = corrected.replace(regex, right);
    });
    
    // Capitalize first letter
    corrected = corrected.charAt(0).toUpperCase() + corrected.slice(1);
    
    // Add question mark if it sounds like a question
    const questionWords = ['what', 'how', 'when', 'where', 'why', 'who', 'which', 'can', 'do', 'is', 'are'];
    const firstWord = corrected.split(' ')[0].toLowerCase();
    if (questionWords.includes(firstWord) && !corrected.endsWith('?')) {
      corrected += '?';
    }
    
    return corrected;
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  };

  return (
    <Box sx={{ 
      height: isEmbedded ? '100%' : '70vh', 
      display: 'flex', 
      flexDirection: 'column',
      background: 'linear-gradient(135deg, #FFF9E6 0%, #FFF0F5 50%, #F0F8FF 100%)',
      position: 'relative'
    }}>
        {/* Header - only show if not embedded */}
        {!isEmbedded && (
          <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider', display: 'flex', alignItems: 'center', gap: 2 }}>
          <Avatar sx={{ bgcolor: 'primary.main' }}>
            <SmartToy />
          </Avatar>
          <Box sx={{ flex: 1 }}>
            <Typography variant="h6">
              {avatarConfig?.name || 'AI Assistant'}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Voice-enabled chat • {speechEnabled ? 'Speech ON' : 'Speech OFF'}
            </Typography>
          </Box>
            <Tooltip title={speechEnabled ? "Disable speech" : "Enable speech"}>
              <IconButton onClick={toggleSpeech} color={speechEnabled ? "primary" : "default"}>
                {speechEnabled ? <VolumeUp /> : <VolumeOff />}
              </IconButton>
            </Tooltip>
          </Box>
        )}

        {/* Messages */}
        <Box sx={{ flex: 1, overflow: 'auto', p: 1 }}>
          <List>
            <AnimatePresence>
              {messages.map((message, index) => (
                <motion.div
                  key={message.id}
                  initial={{ opacity: 0, y: 20, scale: 0.8 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: -20, scale: 0.8 }}
                  transition={{ 
                    type: "spring", 
                    stiffness: 400, 
                    damping: 25,
                    delay: index * 0.1 
                  }}
                >
                  <ListItem
                    sx={{
                      flexDirection: 'column',
                      alignItems: message.sender_type === 'customer' ? 'flex-end' : 'flex-start',
                      mb: 1
                    }}
                  >
                    <Box
                      sx={{
                        maxWidth: '80%',
                        background: message.sender_type === 'customer' 
                          ? 'linear-gradient(135deg, #FF6B9D 0%, #FF8E53 100%)' 
                          : 'linear-gradient(135deg, #FFFFFF 0%, #FFF8DC 100%)',
                        color: message.sender_type === 'customer' ? 'white' : '#5D4037',
                        p: 2.5,
                        borderRadius: 3,
                        borderTopLeftRadius: message.sender_type === 'customer' ? 3 : 0.5,
                        borderTopRightRadius: message.sender_type === 'customer' ? 0.5 : 3,
                        border: message.sender_type === 'customer' ? 'none' : '2px solid #FFD93D',
                        boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
                        position: 'relative',
                        '&::before': message.sender_type !== 'customer' ? {
                          content: '"🍪"',
                          position: 'absolute',
                          top: -8,
                          left: -8,
                          fontSize: '1.2rem',
                          background: '#FFD93D',
                          borderRadius: '50%',
                          width: 24,
                          height: 24,
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.2)'
                        } : {}
                      }}
                    >
                      <Typography variant="body1">{message.content}</Typography>
                    </Box>
                    <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5 }}>
                      {message.sender_type === 'customer' ? 'You' : avatarConfig?.name || 'Assistant'}
                    </Typography>
                  </ListItem>
                </motion.div>
              ))}
            </AnimatePresence>
            {sendMessageMutation.isLoading && (
              <ListItem sx={{ justifyContent: 'flex-start' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, p: 2 }}>
                  <CircularProgress size={16} />
                  <Typography variant="body2" color="text.secondary">
                    Baker Betty is typing...
                  </Typography>
                </Box>
              </ListItem>
            )}
          </List>
          <div ref={messagesEndRef} />
        </Box>

        {/* Input */}
        <Box sx={{ 
          p: 3, 
          borderTop: '3px solid #FFD93D',
          background: 'linear-gradient(135deg, #FFFFFF 0%, #FFF8DC 100%)',
          borderRadius: '16px 16px 0 0'
        }}>
          <Box sx={{ display: 'flex', gap: 1, alignItems: 'flex-end' }}>
            <TextField
              fullWidth
              multiline
              maxRows={3}
              placeholder={isListening ? "Listening..." : "Ask Baker Betty anything..."}
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={isListening || sendMessageMutation.isLoading}
              variant="outlined"
              size="small"
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: '16px',
                  background: 'linear-gradient(135deg, #FFFFFF 0%, #FFF8DC 100%)',
                  border: '2px solid #FFD93D',
                  '&:hover': {
                    borderColor: '#FF8E53',
                  },
                  '&.Mui-focused': {
                    borderColor: '#FF6B9D',
                    boxShadow: '0 0 0 3px rgba(255, 107, 157, 0.2)'
                  }
                }
              }}
            />
            <IconButton
              onClick={isListening ? stopListening : startListening}
              disabled={sendMessageMutation.isLoading}
              sx={{ 
                width: 48,
                height: 48,
                borderRadius: '12px',
                background: isListening 
                  ? 'linear-gradient(135deg, #FF6B9D 0%, #FF8E53 100%)' 
                  : 'linear-gradient(135deg, #FF8E53 0%, #FFD93D 100%)',
                color: 'white',
                border: '2px solid white',
                boxShadow: '0 4px 12px rgba(0,0,0,0.2)',
                '&:hover': { 
                  transform: 'scale(1.1)',
                  boxShadow: '0 6px 16px rgba(0,0,0,0.3)'
                },
                transition: 'all 0.3s ease'
              }}
            >
              {isListening ? <MicOff /> : <Mic />}
            </IconButton>
            <IconButton
              onClick={() => sendMessage()}
              disabled={!inputMessage.trim() || sendMessageMutation.isLoading}
              sx={{
                width: 48,
                height: 48,
                borderRadius: '12px',
                background: 'linear-gradient(135deg, #FFD93D 0%, #FF6B9D 100%)',
                color: 'white',
                border: '2px solid white',
                boxShadow: '0 4px 12px rgba(0,0,0,0.2)',
                '&:hover': { 
                  transform: 'scale(1.1)',
                  boxShadow: '0 6px 16px rgba(0,0,0,0.3)'
                },
                '&:disabled': {
                  background: '#E0E0E0',
                  color: '#999'
                },
                transition: 'all 0.3s ease'
              }}
            >
              <Send />
            </IconButton>
          </Box>
          
          {isListening && (
            <Box sx={{ mt: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
              <motion.div
                animate={{ 
                  scale: [1, 1.2, 1],
                  rotate: [0, 5, -5, 0]
                }}
                transition={{ 
                  repeat: Infinity, 
                  duration: 1.5,
                  ease: "easeInOut"
                }}
              >
                <Chip 
                  icon={<Mic />} 
                  label="🎤 Listening..." 
                  sx={{
                    background: 'linear-gradient(135deg, #FF6B9D 0%, #FF8E53 100%)',
                    color: 'white',
                    fontWeight: 600,
                    border: '2px solid white',
                    boxShadow: '0 4px 12px rgba(255, 107, 157, 0.4)',
                    '& .MuiChip-icon': { color: 'white' }
                  }}
                  size="small"
                />
              </motion.div>
            </Box>
          )}
          
          {isSpeaking && (
            <Box sx={{ mt: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
              <motion.div
                animate={{ 
                  scale: [1, 1.1, 1],
                  y: [0, -2, 0]
                }}
                transition={{ 
                  repeat: Infinity, 
                  duration: 1,
                  ease: "easeInOut"
                }}
              >
                <Chip 
                  icon={<VolumeUp />} 
                  label="💬 Speaking..." 
                  sx={{
                    background: 'linear-gradient(135deg, #FFD93D 0%, #FF8E53 100%)',
                    color: 'white',
                    fontWeight: 600,
                    border: '2px solid white',
                    boxShadow: '0 4px 12px rgba(255, 211, 61, 0.4)',
                    '& .MuiChip-icon': { color: 'white' }
                  }}
                  size="small"
                />
              </motion.div>
            </Box>
          )}
        </Box>

      </Box>
    );
};

export default ChatInterface;