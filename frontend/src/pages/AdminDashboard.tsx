import React from 'react';
import { Box, Container, Typography } from '@mui/material';

const AdminDashboard: React.FC = () => {
  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Admin Dashboard
        </Typography>
        <Typography variant="body1">
          Admin functionality coming soon...
        </Typography>
      </Box>
    </Container>
  );
};

export default AdminDashboard;