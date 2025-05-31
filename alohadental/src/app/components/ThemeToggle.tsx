"use client";
import React from 'react';
import { useTheme, ThemeProvider, createTheme } from '@mui/material/styles';
import IconButton from '@mui/material/IconButton';
import Tooltip from '@mui/material/Tooltip';
import LightModeIcon from '@mui/icons-material/LightMode';
import DarkModeIcon from '@mui/icons-material/DarkMode';
import SettingsBrightnessIcon from '@mui/icons-material/SettingsBrightness';

const THEME_KEY = 'mui-theme-mode';

const getSystemTheme = () => {
  if (typeof window === 'undefined') return 'light';
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
};

export function useColorMode() {
  const [mode, setMode] = React.useState<string>(() => {
    if (typeof window === 'undefined') return 'system';
    return localStorage.getItem(THEME_KEY) || 'system';
  });

  React.useEffect(() => {
    const handler = () => {
      if (mode === 'system') {
        setMode('system');
      }
    };
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', handler);
    return () => window.matchMedia('(prefers-color-scheme: dark)').removeEventListener('change', handler);
  }, [mode]);

  const themeMode = mode === 'system' ? getSystemTheme() : mode;

  const setColorMode = (value: string) => {
    setMode(value);
    localStorage.setItem(THEME_KEY, value);
  };

  return { mode, themeMode, setColorMode };
}

export default function ThemeToggle({ mode, setColorMode }: { mode: string; setColorMode: (mode: string) => void }) {
  return (
    <div className="flex items-center gap-1">
      <Tooltip title="Light Mode">
        <span>
          <IconButton
            color={mode === 'light' ? 'primary' : 'default'}
            onClick={() => setColorMode('light')}
            aria-label="Light mode"
          >
            <LightModeIcon />
          </IconButton>
        </span>
      </Tooltip>
      <Tooltip title="Dark Mode">
        <span>
          <IconButton
            color={mode === 'dark' ? 'primary' : 'default'}
            onClick={() => setColorMode('dark')}
            aria-label="Dark mode"
          >
            <DarkModeIcon />
          </IconButton>
        </span>
      </Tooltip>
      <Tooltip title="System Mode">
        <span>
          <IconButton
            color={mode === 'system' ? 'primary' : 'default'}
            onClick={() => setColorMode('system')}
            aria-label="System mode"
          >
            <SettingsBrightnessIcon />
          </IconButton>
        </span>
      </Tooltip>
    </div>
  );
}
