/* eslint-disable @typescript-eslint/no-explicit-any */
import React from 'react';
import { AppBar, Toolbar, Typography, Chip, Box } from '@mui/material';
import BuildIcon from '@mui/icons-material/Build';
import ShoppingCartIcon from '@mui/icons-material/ShoppingCart';
import { useBuildStore } from '../store/buildStore';

export const Header: React.FC = () => {
  const totalPrice = useBuildStore((state: any) => {
    if (typeof state.getTotalPrice === 'function') {
      return state.getTotalPrice();
    }
    if (typeof state.totalPrice === 'number') {
      return state.totalPrice;
    }
    const components = state.components || [
      state.cpu,
      state.motherboard,
      state.ram,
      state.gpu,
      state.psu,
      state.case ?? state.pcCase,
      state.cooler,
      state.storage,
    ].filter(Boolean);

    if (Array.isArray(components)) {
      return components.reduce((sum: number, item: any) => sum + (Number(item?.price) || 0), 0);
    }
    if (typeof components === 'object') {
      return Object.values(components).reduce((sum: number, item: any) => sum + (Number(item?.price) || 0), 0);
    }
    return 0;
  });

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
          <BuildIcon sx={{ color: '#3f8cff', fontSize: 28 }} />
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
          label={`Total: $${formattedPrice}`}
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
