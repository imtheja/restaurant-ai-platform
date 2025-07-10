import React from 'react';
import { Box, Container, Typography, Button, Card, CardContent } from '@mui/material';
import { useNavigate } from 'react-router-dom';

const LandingPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 8, textAlign: 'center' }}>
        <Typography variant="h2" component="h1" gutterBottom>
          Restaurant AI Platform
        </Typography>
        <Typography variant="h5" component="h2" gutterBottom sx={{ mb: 4 }}>
          Experience the future of dining with AI-powered restaurant assistants
        </Typography>
        
        <Card sx={{ maxWidth: 600, mx: 'auto', mb: 4 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              🍪 Try our sample restaurant:
            </Typography>
            <Typography variant="body1" sx={{ mb: 2 }}>
              Chip Cookies - Warm fresh gourmet cookies delivered to your door
            </Typography>
            <Button 
              variant="contained" 
              size="large"
              onClick={() => navigate('/r/chip-cookies')}
            >
              Visit Chip Cookies
            </Button>
          </CardContent>
        </Card>

        <Typography variant="body1" color="text.secondary">
          AI-powered conversations • Smart menu recommendations • Seamless ordering
        </Typography>
      </Box>
    </Container>
  );
};

export default LandingPage;