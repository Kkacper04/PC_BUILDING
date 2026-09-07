import React from 'react';
import { AppBar, Toolbar, Typography, Chip, Box } from '@mui/material';
import ShoppingCartIcon from '@mui/icons-material/ShoppingCart';
import { useBuildStore } from '../store/buildStore';

export const Header: React.FC = () => {
  const totalPrice = useBuildStore((state) => state.getTotalPrice());

  const formattedPrice = Number(totalPrice || 0).toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });

  return (
    <AppBar
      position="static"
      elevation={2}
      sx={{
        backgroundColor: '#1c1c1c',
        borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
      }}
    >
      <Toolbar sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
          <Typography
            variant="h6"
            component="div"
            sx={{
              fontWeight: 700,
              letterSpacing: 0.5,
              color: '#ffffff',
              userSelect: 'none',
            }}
          >
            PC Builder
          </Typography>
        </Box>

        <Chip
          icon={<ShoppingCartIcon sx={{ fontSize: 18, color: '#ffffff !important' }} />}
          label={`Total: ${formattedPrice} zł`}
          color="primary"
          sx={{
            fontWeight: 600,
            fontSize: '0.95rem',
            px: 1,
            py: 2,
            backgroundColor: '#3f8cff',
            '&:hover': {
              backgroundColor: '#3173d6',
            },
          }}
        />
      </Toolbar>
    </AppBar>
  );
};

export default Header;
