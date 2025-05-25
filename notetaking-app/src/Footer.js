import React from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import IconButton from '@mui/material/IconButton';
import GitHubIcon from '@mui/icons-material/GitHub';
import Tooltip from '@mui/material/Tooltip';

const Footer = () => {
  return (
    <Box
      component="footer"
      sx={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        py: 2,
        mt: 4,
        background: 'linear-gradient(90deg, #2575fc 0%, #6a11cb 100%)',
        color: 'white',
        position: 'relative',
        bottom: 0,
        width: '100%'
      }}
    >
      <Typography variant="body2" sx={{ mr: 1 }}>
        © {new Date().getFullYear()} NoteTaking App
      </Typography>
      <Tooltip title="View on GitHub">
        <IconButton
          color="inherit"
          href="https://github.com/"
          target="_blank"
          rel="noopener noreferrer"
          size="small"
        >
          <GitHubIcon />
        </IconButton>
      </Tooltip>
    </Box>
  );
};

export default Footer;
