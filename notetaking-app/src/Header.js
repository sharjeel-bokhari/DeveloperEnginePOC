import React from 'react';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import IconButton from '@mui/material/IconButton';
import MenuIcon from '@mui/icons-material/Menu';
import Tooltip from '@mui/material/Tooltip';
import Avatar from '@mui/material/Avatar';
import { deepPurple } from '@mui/material/colors';

const Header = () => {
  return (
    <AppBar position="static" sx={{ mb: 3, background: 'linear-gradient(90deg, #6a11cb 0%, #2575fc 100%)' }}>
      <Toolbar>
        <Tooltip title="Open menu">
          <IconButton edge="start" color="inherit" aria-label="menu" sx={{ mr: 2 }}>
            <MenuIcon />
          </IconButton>
        </Tooltip>
        <Typography variant="h5" component="div" sx={{ flexGrow: 1, fontWeight: 700, letterSpacing: 1 }}>
          NoteTaking App
        </Typography>
        <Tooltip title="Your Profile">
          <Avatar sx={{ bgcolor: deepPurple[500], cursor: 'pointer' }}>N</Avatar>
        </Tooltip>
      </Toolbar>
    </AppBar>
  );
};

export default Header;
