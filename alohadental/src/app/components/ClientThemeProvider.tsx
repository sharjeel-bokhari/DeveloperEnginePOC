"use client";
import React from "react";
import { ThemeProvider, createTheme, CssBaseline } from "@mui/material";
import { useColorMode } from "./ThemeToggle";
import Header from "./Header";
import Footer from "./Footer";

export default function ClientThemeProvider({ children }: { children: React.ReactNode }) {
  const { mode, themeMode, setColorMode } = useColorMode();
  const theme = React.useMemo(
    () =>
      createTheme({
        palette: {
          mode: themeMode as "light" | "dark",
          primary: { main: "#1976d2" },
        },
      }),
    [themeMode]
  );
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Header mode={mode} setColorMode={setColorMode} />
      <main className="min-h-[80vh]">{children}</main>
      <Footer />
    </ThemeProvider>
  );
}
