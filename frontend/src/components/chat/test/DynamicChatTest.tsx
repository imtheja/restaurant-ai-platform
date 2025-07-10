import React from 'react';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Box, Typography } from '@mui/material';
import DynamicChatInterface from '../DynamicChatInterface';

// Create test query client
const testQueryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
      refetchOnWindowFocus: false,
    },
  },
});

const DynamicChatTest: React.FC = () => {
  return (
    <QueryClientProvider client={testQueryClient}>
      <Box sx={{ height: '100vh', p: 2 }}>
        <Typography variant="h4" gutterBottom>
          🧪 Dynamic Chat Interface Test
        </Typography>
        
        <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
          Testing the new dynamic chat interface that adapts based on AI configuration.
        </Typography>
        
        <Box sx={{ 
          height: '70vh', 
          border: '2px solid #E0E0E0', 
          borderRadius: '12px', 
          overflow: 'hidden' 
        }}>
          <DynamicChatInterface
            restaurantSlug="test-restaurant"
            onChatReady={(sendMessage) => {
              console.log('Test: Chat is ready!', sendMessage);
            }}
            isEmbedded={false}
          />
        </Box>
      </Box>
    </QueryClientProvider>
  );
};

export default DynamicChatTest;