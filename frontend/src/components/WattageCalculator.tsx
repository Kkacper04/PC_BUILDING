import React from 'react';
import { Box, Typography, LinearProgress, Stack } from '@mui/material';
import BoltIcon from '@mui/icons-material/Bolt';
import type { CPUResponse, GPUResponse, PSUResponse } from '../types/api';

interface WattageCalculatorProps {
  cpu: CPUResponse | null;
  gpu: GPUResponse | null;
  psu: PSUResponse | null;
}

const SYSTEM_OVERHEAD_WATTS = 50;

export const WattageCalculator: React.FC<WattageCalculatorProps> = ({ cpu, gpu, psu }) => {
  const cpuTdp = cpu?.tdp ?? 0;
  const gpuTdp = gpu?.tdp ?? 0;
  const estimatedWattage = cpuTdp + gpuTdp + SYSTEM_OVERHEAD_WATTS;
  const psuWattage = psu?.wattage ?? 0;

  const hasAnyComponent = cpu || gpu;
  if (!hasAnyComponent) return null;

  const usagePercent = psuWattage > 0 ? Math.min((estimatedWattage / psuWattage) * 100, 100) : 0;

  const getBarColor = (): 'success' | 'warning' | 'error' => {
    if (!psu) return 'warning';
    if (usagePercent > 90) return 'error';
    if (usagePercent > 75) return 'warning';
    return 'success';
  };

  const getStatusText = (): string => {
    if (!psu) return 'Select a PSU to see headroom';
    if (estimatedWattage > psuWattage) return 'PSU wattage is insufficient!';
    const headroom = psuWattage - estimatedWattage;
    return `${headroom}W headroom`;
  };

  return (
    <Box
      sx={{
        mt: 2,
        p: 2,
        backgroundColor: 'rgba(255, 255, 255, 0.03)',
        borderRadius: 2,
        border: '1px solid rgba(255, 255, 255, 0.08)',
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1.5 }}>
        <BoltIcon sx={{ color: 'primary.main', fontSize: 20 }} />
        <Typography variant="subtitle2" sx={{ fontWeight: 700 }}>
          Estimated Power Draw
        </Typography>
      </Box>

      <Stack spacing={0.5} sx={{ mb: 1.5 }}>
        {cpu && (
          <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
            <Typography variant="caption" color="text.secondary">CPU</Typography>
            <Typography variant="caption" color="text.primary">{cpuTdp}W</Typography>
          </Box>
        )}
        {gpu && (
          <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
            <Typography variant="caption" color="text.secondary">GPU</Typography>
            <Typography variant="caption" color="text.primary">{gpuTdp}W</Typography>
          </Box>
        )}
        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
          <Typography variant="caption" color="text.secondary">System (mobo, fans, drives)</Typography>
          <Typography variant="caption" color="text.primary">{SYSTEM_OVERHEAD_WATTS}W</Typography>
        </Box>
      </Stack>

      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', mb: 0.5 }}>
        <Typography variant="body2" sx={{ fontWeight: 700 }}>
          {estimatedWattage}W
        </Typography>
        {psu && (
          <Typography variant="body2" color="text.secondary">
            / {psuWattage}W
          </Typography>
        )}
      </Box>

      <LinearProgress
        variant="determinate"
        value={psu ? usagePercent : 0}
        color={getBarColor()}
        sx={{
          height: 8,
          borderRadius: 4,
          backgroundColor: 'rgba(255, 255, 255, 0.08)',
        }}
      />

      <Typography
        variant="caption"
        color={getBarColor() === 'error' ? 'error.main' : 'text.secondary'}
        sx={{ mt: 0.5, display: 'block' }}
      >
        {getStatusText()}
      </Typography>
    </Box>
  );
};

export default WattageCalculator;
