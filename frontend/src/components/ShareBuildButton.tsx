import React, { useState } from 'react';
import { Button, Snackbar, Alert } from '@mui/material';
import ShareIcon from '@mui/icons-material/Share';
import { encodeBuildToUrl } from '../utils/shareBuild';

interface ShareBuildButtonProps {
  buildIds: {
    cpu?: number;
    motherboard?: number;
    ram?: number;
    gpu?: number;
    psu?: number;
    case?: number;
    cooler?: number;
    storage?: number;
  };
  disabled?: boolean;
}

export const ShareBuildButton: React.FC<ShareBuildButtonProps> = ({ buildIds, disabled }) => {
  const [snackOpen, setSnackOpen] = useState(false);

  const handleShare = async () => {
    const url = encodeBuildToUrl(buildIds);
    try {
      await navigator.clipboard.writeText(url);
      setSnackOpen(true);
    } catch {
      const input = document.createElement('input');
      input.value = url;
      document.body.appendChild(input);
      input.select();
      document.execCommand('copy');
      document.body.removeChild(input);
      setSnackOpen(true);
    }
  };

  return (
    <>
      <Button
        fullWidth
        variant="outlined"
        color="primary"
        onClick={handleShare}
        disabled={disabled}
        startIcon={<ShareIcon />}
        sx={{
          fontWeight: 600,
          borderColor: 'primary.main',
          '&:hover': {
            borderColor: 'primary.light',
            backgroundColor: 'rgba(249, 115, 22, 0.08)',
          },
        }}
      >
        Share Build
      </Button>

      <Snackbar
        open={snackOpen}
        autoHideDuration={3000}
        onClose={() => setSnackOpen(false)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert
          onClose={() => setSnackOpen(false)}
          severity="success"
          variant="filled"
          sx={{ width: '100%' }}
        >
          Build link copied to clipboard!
        </Alert>
      </Snackbar>
    </>
  );
};

export default ShareBuildButton;
